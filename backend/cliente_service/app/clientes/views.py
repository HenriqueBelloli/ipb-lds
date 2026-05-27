from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from shared.auth_middleware.permissions import IsOperador
from .models import Cliente, ClienteDelegacao
from .serializers import (
    ClienteSerializer, ClienteDetailSerializer, ClienteDelegacaoSerializer
)
from shared.rabbitmq import publish_event
from .services.financeiro_client import FinanceiroServiceClient


class ClienteListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOperador]

    def get_serializer_class(self):
        return ClienteSerializer

    @extend_schema(
            responses={200:ClienteSerializer}
    )
    def get_queryset(self):
        queryset = Cliente.objects.all()
        nome = self.request.query_params.get('nome')
        nif = self.request.query_params.get('nif')
        flag_associado = self.request.query_params.get('flagAssociado')
        delegacao_id = self.request.query_params.get('delegacaoId')
        ativo = self.request.query_params.get('ativo')

        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if nif:
            queryset = queryset.filter(nif__icontains=nif)
        if flag_associado is not None:
            queryset = queryset.filter(
                flagAssociado=flag_associado.lower() == 'true'
            )
        if delegacao_id:
            ids = ClienteDelegacao.objects.filter(
                delegacaoId=delegacao_id
            ).values_list('clienteId', flat=True)
            queryset = queryset.filter(id__in=ids)
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo.lower() == 'true')

        return queryset

    @extend_schema(
            request=ClienteSerializer,
            responses={201: ClienteSerializer}
    )
    def perform_create(self, serializer):
        cliente = serializer.save()
        publish_event('cliente.criado', {
            'servico': 'cliente-service',
            'clienteId': str(cliente.id),
            'nome': cliente.nome,
            'nif': cliente.nif,
            'flagAssociado': cliente.flagAssociado,
            'usuarioId': self.request.auth.get('usuarioId'),
            'delegacaoId': self.request.auth.get('delegacaoId'),
        })


class ClienteDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsOperador]
    queryset = Cliente.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClienteDetailSerializer
        return ClienteSerializer

    @extend_schema(
            responses={ClienteDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        cliente = self.get_object()
        token = request.headers.get(
            'Authorization', ''
        ).replace('Bearer ', '')
        inadimplente = FinanceiroServiceClient.verificar_inadimplente(
            str(cliente.id), token
        )
        serializer = ClienteDetailSerializer(
            cliente,
            context={'inadimplente': inadimplente, 'request': request}
        )
        return Response(serializer.data)


class ClienteDelegacaoView(APIView):
    permission_classes = [IsOperador]

    @extend_schema(
            responses={200: ClienteDelegacaoSerializer}
    )
    def get(self, request, pk):
        get_object_or_404(Cliente, pk=pk)
        delegacoes = ClienteDelegacao.objects.filter(clienteId=pk)
        serializer = ClienteDelegacaoSerializer(delegacoes, many=True)
        return Response(serializer.data)

    @extend_schema(
            responses= {201: ClienteDelegacaoSerializer,
                        200: ClienteDelegacaoSerializer}
    )
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        delegacao_id = request.data.get('delegacaoId')
        if not delegacao_id:
            return Response(
                {'erro': 'delegacaoId é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj, created = ClienteDelegacao.objects.get_or_create(
            clienteId=cliente,
            delegacaoId=delegacao_id
        )
        serializer = ClienteDelegacaoSerializer(obj)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
