from django.shortcuts import get_object_or_404
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, AllowAny
from .serializers import *
from rest_framework import status

# Create your views here.

class ContasReceberListView(APIView):

    #GET /api/financeiro/contas-receber/ - FINANCEIRO
    #GET .../contas-receber/{id} - FINANCEIRO
    #PATCH .../contas-receber/{id}/faturar/ - FINANCEIRO
    #GET .../contas-receber/entrada-paga/{osId} - Interno
    
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
    
    permission_classes = [AllowAny]

    def _get_object(self, pk):
        return get_object_or_404(ContaReceber, pk=pk)

    def get(self, request, pk):
        conta = self._get_object(pk)
        serializer = ContasReceberListSerializer(conta, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)
        

class ContasReceberUpdateView(APIView):
    pass

class ContasReceberVerifyEntradaView(APIView):
    pass


