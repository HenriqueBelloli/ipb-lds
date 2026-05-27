from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.auth_middleware.permissions import IsOperador, IsFinanceiro

from .models import OrdemServico, OrdemServicoHistorico
from .serializers import (
    OrdemServicoSerializer,
    OrdemServicoCreateSerializer,
    OrdemServicoHistoricoSerializer,
)
from .state_machine import validar_transicao
from .publisher import publish_event
from .services.financeiro_client import FinanceiroServiceClient


def _token_from_request(request) -> str:
    return request.headers.get('Authorization', '').replace('Bearer ', '')


class OrdemServicoListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOperador]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrdemServicoCreateSerializer
        return OrdemServicoSerializer

    def get_queryset(self):
        qs = OrdemServico.objects.all()
        params = self.request.query_params
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        if params.get('delegacaoId'):
            qs = qs.filter(delegacaoExecucaoId=params['delegacaoId'])
        if params.get('clienteId'):
            qs = qs.filter(clienteId=params['clienteId'])
        if params.get('tipoPreco'):
            qs = qs.filter(tipoPreco=params['tipoPreco'])
        return qs

    @transaction.atomic
    def perform_create(self, serializer):
        usuario_id = self.request.auth.get('usuarioId')
        delegacao_id = self.request.auth.get('delegacaoId')

        os = serializer.save(
            usuarioCriacaoId=usuario_id,
            delegacaoContratacaoId=delegacao_id,
        )

        OrdemServicoHistorico.objects.create(
            ordemServicoId=os,
            usuarioId=usuario_id,
            statusAnterior=None,
            statusNovo=os.status,
            observacao='OS criada',
        )

        publish_event('os.criada', {
            'servico': 'os-service',
            'osId': str(os.id),
            'clienteId': str(os.clienteId),
            'delegacaoId': str(os.delegacaoExecucaoId),
            'status': os.status,
            'valorTotal': str(os.valorTotal),
            'usuarioId': str(usuario_id),
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        os_obj = serializer.instance
        return Response(
            OrdemServicoSerializer(os_obj).data,
            status=status.HTTP_201_CREATED,
        )


class OrdemServicoDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsOperador]
    serializer_class = OrdemServicoSerializer
    queryset = OrdemServico.objects.all()


class OrdemServicoStatusView(APIView):
    permission_classes = [IsOperador]

    @transaction.atomic
    def patch(self, request, pk):
        os = get_object_or_404(OrdemServico, pk=pk)
        novo_status = request.data.get('status')
        observacao = request.data.get('observacao', '')
        usuario_id = request.auth.get('usuarioId')
        token = _token_from_request(request)

        if not novo_status:
            return Response(
                {'erro': 'Campo status é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not validar_transicao(os.status, novo_status):
            return Response(
                {'erro': f'Transição de {os.status} para {novo_status} não permitida.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if os.status == 'PAGAMENTO_PENDENTE' and novo_status == 'A_EXECUTAR':
            try:
                entrada_paga = FinanceiroServiceClient.verificar_entrada_paga(str(pk), token)
            except Exception as e:
                return Response(
                    {'erro': str(e)},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            if not entrada_paga:
                return Response(
                    {'erro': 'Pagamento de entrada pendente. Regularize no módulo financeiro antes de avançar.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        status_anterior = os.status
        os.status = novo_status
        os.save()

        OrdemServicoHistorico.objects.create(
            ordemServicoId=os,
            usuarioId=usuario_id,
            statusAnterior=status_anterior,
            statusNovo=novo_status,
            observacao=observacao,
        )

        if status_anterior == 'AGUARDA_APROVACAO' and novo_status in ('PAGAMENTO_PENDENTE', 'A_EXECUTAR'):
            itens = list(os.itens.values('servicoId', 'servicoDelegacaoId', 'precoAplicado'))
            publish_event('os.aprovada', {
                'servico': 'os-service',
                'osId': str(os.id),
                'clienteId': str(os.clienteId),
                'itens': [{k: str(v) for k, v in item.items()} for item in itens],
                'valorTotal': str(os.valorTotal),
                'statusResultante': novo_status,
                'usuarioId': str(usuario_id),
            })
        elif novo_status == 'CONCLUIDO':
            publish_event('os.concluida', {
                'servico': 'os-service',
                'osId': str(os.id),
                'clienteId': str(os.clienteId),
                'valorTotal': str(os.valorTotal),
                'usuarioId': str(usuario_id),
            })

        publish_event('os.status.atualizado', {
            'servico': 'os-service',
            'osId': str(os.id),
            'statusAnterior': status_anterior,
            'statusNovo': novo_status,
            'usuarioId': str(usuario_id),
        })

        return Response(OrdemServicoSerializer(os).data)


class OrdemServicoCancelarView(APIView):
    permission_classes = [IsOperador]

    @transaction.atomic
    def patch(self, request, pk):
        os = get_object_or_404(OrdemServico, pk=pk)
        motivo = request.data.get('motivo', '')
        usuario_id = request.auth.get('usuarioId')
        token = _token_from_request(request)

        if os.status == 'FATURADO':
            return Response(
                {'erro': 'Não é possível cancelar uma OS já faturada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if os.status == 'CANCELADO':
            return Response(
                {'erro': 'A OS já se encontra cancelada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tem_pagamentos = FinanceiroServiceClient.verificar_pagamentos_os(str(pk), token)
        if tem_pagamentos:
            return Response(
                {'erro': 'Existem pagamentos registados para esta OS. Regularize no módulo financeiro antes de cancelar.'},
                status=status.HTTP_409_CONFLICT,
            )

        status_anterior = os.status
        os.status = 'CANCELADO'
        os.motivoCancelamento = motivo
        os.save()

        OrdemServicoHistorico.objects.create(
            ordemServicoId=os,
            usuarioId=usuario_id,
            statusAnterior=status_anterior,
            statusNovo='CANCELADO',
            observacao=motivo,
        )

        publish_event('os.cancelada', {
            'servico': 'os-service',
            'osId': str(os.id),
            'clienteId': str(os.clienteId),
            'motivo': motivo,
            'usuarioId': str(usuario_id),
            'delegacaoId': str(os.delegacaoExecucaoId),
        })

        return Response(OrdemServicoSerializer(os).data)


class OrdemServicoHistoricoView(generics.ListAPIView):
    permission_classes = [IsOperador]
    serializer_class = OrdemServicoHistoricoSerializer

    def get_queryset(self):
        os_id = self.kwargs['pk']
        get_object_or_404(OrdemServico, pk=os_id)
        return OrdemServicoHistorico.objects.filter(
            ordemServicoId=os_id,
        ).order_by('createdAt')


class OrdemServicoPorDelegacaoView(generics.ListAPIView):
    permission_classes = [IsOperador]
    serializer_class = OrdemServicoSerializer

    def get_queryset(self):
        delegacao_id = self.kwargs['delegacaoId']
        return OrdemServico.objects.filter(delegacaoExecucaoId=delegacao_id)
