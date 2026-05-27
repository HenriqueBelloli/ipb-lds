from rest_framework import generics, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.shortcuts import get_object_or_404
from shared.auth_middleware.permissions import IsOperador
from shared.auth_middleware.drf_authentication import JWTStatelessAuthentication
from shared.auth_middleware.internal_auth import InternalServiceAuthentication
from .models import Cliente, ClienteDelegacao
from .serializers import (
    ClienteSerializer, ClienteDetailSerializer, ClienteDelegacaoSerializer
)
from .publishers import publish_cliente_criado
from .services.financeiro_client import FinanceiroServiceClient
from .services.usuario_client import UsuarioServiceClient


@extend_schema_view(
    list=extend_schema(
        summary='Listar clientes',
        tags=['clientes'],
        parameters=[
            OpenApiParameter('nome', OpenApiTypes.STR, description='Filtrar por nome (parcial)'),
            OpenApiParameter('nif', OpenApiTypes.STR, description='Filtrar por NIF (parcial)'),
            OpenApiParameter('delegacaoId', OpenApiTypes.UUID, description='Filtrar por delegação'),
            OpenApiParameter('flagAssociado', OpenApiTypes.BOOL, description='Filtrar por associado'),
            OpenApiParameter('ativo', OpenApiTypes.BOOL, description='Filtrar por estado activo'),
        ],
        responses={200: ClienteSerializer},
    ),
    create=extend_schema(
        summary='Criar cliente',
        tags=['clientes'],
        request=ClienteSerializer,
        responses={201: ClienteSerializer},
    ),
)
class ClienteListCreateView(generics.ListCreateAPIView):
    authentication_classes = [InternalServiceAuthentication, JWTStatelessAuthentication]
    permission_classes = [IsOperador]

    def get_serializer_class(self):
        return ClienteSerializer

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

    def perform_create(self, serializer):
        cliente = serializer.save()
        publish_cliente_criado(
            cliente,
            self.request.auth.get('usuarioId'),
            self.request.auth.get('delegacaoId'),
        )


@extend_schema_view(
    retrieve=extend_schema(
        summary='Detalhe do cliente',
        tags=['clientes'],
        responses={200: ClienteDetailSerializer},
    ),
    update=extend_schema(
        summary='Actualizar cliente',
        tags=['clientes'],
        request=ClienteSerializer,
        responses={200: ClienteSerializer},
    ),
)
class ClienteDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsOperador]
    queryset = Cliente.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClienteDetailSerializer
        return ClienteSerializer

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
        summary='Listar delegações do cliente',
        tags=['clientes'],
        responses={
            200: inline_serializer(
                name='DelegacaoDoClienteResponse',
                fields={
                    'delegacaoId': serializers.UUIDField(),
                    'nome': serializers.CharField(),
                },
                many=True,
            )
        },
    )
    def get(self, request, pk):
        get_object_or_404(Cliente, pk=pk)
        delegacoes = ClienteDelegacao.objects.filter(clienteId=pk)

        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        nomes = UsuarioServiceClient.mapa_nomes_delegacoes(token)

        result = sorted(
            [
                {'delegacaoId': str(d.delegacaoId), 'nome': nomes.get(str(d.delegacaoId), str(d.delegacaoId))}
                for d in delegacoes
            ],
            key=lambda x: x['nome'],
        )
        return Response(result)

    @extend_schema(
        summary='Associar cliente a delegação',
        tags=['clientes'],
        request=inline_serializer(
            name='AssociarDelegacaoRequest',
            fields={'delegacaoId': serializers.UUIDField()},
        ),
        responses={201: ClienteDelegacaoSerializer, 200: ClienteDelegacaoSerializer},
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
