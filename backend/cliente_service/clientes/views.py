from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cliente, ClienteDelegacao
from .serializers import (
    ClienteSerializer,
    ClienteDetalheSerializer,
    AssociaDelegacaoSerializer,
)
from .services import obter_inadimplencia
from .permissions import IsAuthenticatedViaJWT


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.prefetch_related('delegacoes').all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticatedViaJWT]

    def get_queryset(self):
        qs = super().ger_queryset()
        ativo = self.request.query_params.get('ativo')
        if ativo is not None:
            qs = qs.filter(ativo=ativo.lower() == 'true')
            return qs
        
    def retrieve(self, request, *args, **kwargs):
        client = self.get_object()

        dados_financeiros = obter_inadimplencia(str(client.id))

        data = ClienteDetalheSerializer(client).data
        data['inadimplente'] = dados_financeiros.get('inadimplente') if dados_financeiros else None
        data['divida_total'] = dados_financeiros.get('divida_total') if dados_financeiros else None

        return Response(data)
    @action(detail=True, methods=['post'], url_path='delegacoes')
    def associar_delegacao(self, request, pk=None):
        cliente = self.get_object()
        serializer = AssociarDelegacaoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
        delegacao_id = serializer.validated_data['delegacaoId']

        if ClienteDelegacao.objects.filter(clienteId=cliente, delegacaoId=delegacao_id).exists():
            return Response({'datail': 'Associação já existe.'}, status=status.HTTP_409_CONFLICT)
    @action(detail=True, methods=['delete'], url_path='delegacoes/(?P<delegacao_id>[^/.]+)')
    def remover_delegacao(self, reques, pk=None, delegacao_id=None):
        cliente = self.get_object()
        deleted, _ = ClienteDelegacao.objects.filter(
            clienteId=cliente, delegacaoId=delegacao_id).delete()

        if not deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
    
