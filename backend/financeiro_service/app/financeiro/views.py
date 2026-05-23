from django.shortcuts import get_object_or_404
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, AllowAny
from .serializers import *
from rest_framework import status
from .services.faturacao_service import FaturacaoService
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your views here.

class ContasReceberListView(APIView):

    #perfil minimo = financeiro
    
    permission_classes = [AllowAny]

    def get(self, request):
        qs = ContaReceber.objects.all()

        cliente_id = request.query_params.get('clienteId')
        ordemServico_id = request.query_params.get('ordemServicoId')
        tipo = request.query_params.get('tipo')
        valor = request.query_params.get('valor')
        valorPago = request.query_params.get('valorPago')
        _status = request.query_params.get('status')
        dataVencimento = request.query_params.get('dataVencimento')


        if cliente_id:
            qs = qs.filter(cliente_id = cliente_id)
        
        if ordemServico_id:
            qs = qs.filter(ordemServico_id = ordemServico_id)
        
        if tipo:
            qs = qs.filter(tipo = tipo)
        
        if valor:
            qs = qs.filter(valor = valor)
        
        if valorPago:
            qs = qs.filter(valorPago = valorPago)

        if _status:
            qs = qs.filter(status = _status)
        
        if dataVencimento:
            qs = qs.filter(dataVencimento = dataVencimento)
        
        serializer = ContasReceberListSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class ContasReceberDetailView(APIView):
    #perfil minimo = financeiro
    permission_classes = [AllowAny]

    def _get_object(self, pk):
        return get_object_or_404(ContaReceber, pk=pk)

    def get(self, request, pk):
        conta = self._get_object(pk)
        serializer = ContasReceberListSerializer(conta, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)
        

class ContasReceberFaturarView(APIView):
    #perfil minimo = financeiro
    permission_classes = [AllowAny]

    def _get_object(self, pk):
        return get_object_or_404(ContaReceber, pk=pk)
    
    def patch(self, request, pk):
        conta = self._get_object(pk)
        id = conta.id

        try:
            saldo_final = FaturacaoService.faturar(id)
        except ValidationError as e:
            return Response(
                data = {'message': e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ContasReceberListSerializer(saldo_final)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
     

class ClienteInadimplenteView(APIView):
    #perfil minimo = Interno
    def get(self, request, clienteId):
        hoje = timezone.now().date()

        inadimplente = ContaReceber.objects.filter(
            clienteId=clienteId,
            tipo='MENSALIDADE',
            status__in=['ABERTA', 'VENCIDA'],
            dataVencimento__year=hoje.year,
            dataVencimento__month=hoje.month
        ).exists()

        return Response({'inadimplente': inadimplente}, status=status.HTTP_200_OK)


class VerificarEntradaPagaView(APIView):
    #perfil minimo = interno

    def _get_object(self, osId) -> ContaReceber:
        return get_object_or_404(
            ContaReceber,
            ordemServicoId = osId,
            tipo = 'ENTRADA'
        )

    def get(self, request, osId):
        
        conta = self._get_object(osId)

        entrada_paga = conta.status == 'PAGA'

        return Response({'Entrada paga':entrada_paga}, status=status.HTTP_200_OK)




