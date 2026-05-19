from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Cliente, ClienteDelegacao
from .serializers import (
    ClienteSerializer,
    ClienteDetalheSerializer,
    ClienteDelegacaoSerializer,
    AssociarDelegacaoSerializer,
)
from .services import FinanceiroServiceClient
from .permissions import JWTAuthentication, IsOperador


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'associar_delegacao'):
            return [IsOperador()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Cliente.objects.all()
        params = self.request.query_params

        nome = params.get('nome')
        nif = params.get('nif')
        flag_associado = params.get('flagAssociado')
        delegacao_id = params.get('delegacaoId')
        ativo = params.get('ativo')

        if nome:
            qs = qs.filter(nome__icontains=nome)
        if nif:
            qs = qs.filter(nif__icontains=nif)
        if flag_associado is not None:
            qs = qs.filter(flagAssociado=flag_associado.lower() == 'true')
        if delegacao_id:
            ids = ClienteDelegacao.objects.filter(
                delegacaoId=delegacao_id
            ).values_list('clienteId', flat=True)
            qs = qs.filter(id__in=ids)
        if ativo is not None:
            qs = qs.filter(ativo=ativo.lower() == 'true')

        return qs.order_by('-createdAt')

    def retrieve(self, request, *args, **kwargs):
        cliente = self.get_object()
        # ⚠ PONTO DE REVISÃO SÉNIOR — ver services/financeiro_client.py
        token = request.auth or ''
        inadimplente = FinanceiroServiceClient.verificar_inadimplente(
            str(cliente.id), token
        )
        serializer = ClienteDetalheSerializer(
            cliente,
            context={'inadimplente': inadimplente, 'request': request},
        )
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get', 'post'], url_path='delegacoes')
    def delegacoes(self, request, pk=None):
        cliente = self.get_object()

        if request.method == 'GET':
            qs = ClienteDelegacao.objects.filter(clienteId=cliente)
            return Response(ClienteDelegacaoSerializer(qs, many=True).data)

        # POST
        serializer = AssociarDelegacaoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        delegacao_id = serializer.validated_data['delegacaoId']
        obj, created = ClienteDelegacao.objects.get_or_create(
            clienteId=cliente,
            delegacaoId=delegacao_id,
        )
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(ClienteDelegacaoSerializer(obj).data, status=status_code)