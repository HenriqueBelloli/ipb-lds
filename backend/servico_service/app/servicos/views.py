from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from shared.auth_middleware.permissions import IsOperador, IsGestor, IsAdministrador
from .models import Servico, ServicoDelegacao
from .serializers import ServicoSerializer, ServicoDelegacaoSerializer


class ServicoListCreateView(generics.ListCreateAPIView):
    serializer_class = ServicoSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdministrador()]
        return [IsOperador()]

    def get_queryset(self):
        queryset = Servico.objects.all()
        nome = self.request.query_params.get('nome')
        flag_bonificavel = self.request.query_params.get('flagBonificavel')
        ativo = self.request.query_params.get('ativo')

        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if flag_bonificavel is not None:
            queryset = queryset.filter(
                flagBonificavel=flag_bonificavel.lower() == 'true'
            )
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo.lower() == 'true')
        return queryset

    @extend_schema(
        description="Listar catálogo global de serviços com filtros opcionais",
        parameters=[
            OpenApiParameter('nome', str, description="Filtro por nome (icontains)"),
            OpenApiParameter('flagBonificavel', str, description="Filtro por bonificável (true/false)"),
            OpenApiParameter('ativo', str, description="Filtro por ativo (true/false)"),
        ],
        responses={200: ServicoSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """Lista todos os serviços do catálogo global. Requer perfil OPERADOR ou superior."""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Criar novo tipo de serviço no catálogo global",
        request=ServicoSerializer,
        responses={201: ServicoSerializer}
    )
    def post(self, request, *args, **kwargs):
        """Cria um novo serviço. Requer perfil ADMINISTRADOR."""
        return super().post(request, *args, **kwargs)


class ServicoDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ServicoSerializer
    queryset = Servico.objects.all()

    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsAdministrador()]
        return [IsOperador()]

    @extend_schema(
        description="Obter detalhe de um serviço pelo ID",
        responses={200: ServicoSerializer}
    )
    def get(self, request, *args, **kwargs):
        """Retorna os dados completos de um serviço. Requer perfil OPERADOR ou superior."""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Atualizar dados de um serviço, incluindo o campo ativo",
        request=ServicoSerializer,
        responses={200: ServicoSerializer}
    )
    def put(self, request, *args, **kwargs):
        """Atualiza um serviço. Requer perfil ADMINISTRADOR."""
        return super().put(request, *args, **kwargs)


class ServicoDelegacaoListCreateView(generics.ListCreateAPIView):
    serializer_class = ServicoDelegacaoSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsGestor()]
        return [IsOperador()]

    def get_queryset(self):
        delegacao_id = self.kwargs.get('delegacaoId')
        queryset = ServicoDelegacao.objects.filter(
            delegacaoId=delegacao_id
        ).select_related('servicoId')

        ativo = self.request.query_params.get('ativo')
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo.lower() == 'true')
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tipoPreco'] = self.request.query_params.get('tipoPreco')
        return context

    @extend_schema(
        description="Listar serviços disponíveis numa delegação específica com preços",
        parameters=[
            OpenApiParameter('tipoPreco', str, description="ASSOCIADO ou NAO_ASSOCIADO para calcular precoAplicado"),
            OpenApiParameter('ativo', str, description="Filtro por ativo (true/false)"),
        ],
        responses={200: ServicoDelegacaoSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """Retorna os serviços configurados numa delegação com preços. 
        O parâmetro tipoPreco calcula precoAplicado automaticamente.
        Requer perfil OPERADOR ou superior."""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Configurar um serviço numa delegação específica com preços e percentual de entrada",
        request=ServicoDelegacaoSerializer,
        responses={201: ServicoDelegacaoSerializer}
    )
    def post(self, request, *args, **kwargs):
        """Configura um serviço numa delegação com preços e percentual de entrada.
        Requer perfil GESTOR ou superior."""
        return super().post(request, *args, **kwargs)


class ServicoDelegacaoDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ServicoDelegacaoSerializer
    queryset = ServicoDelegacao.objects.select_related('servicoId')

    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsGestor()]
        return [IsOperador()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tipoPreco'] = self.request.query_params.get('tipoPreco')
        return context

    @extend_schema(
        description="Obter detalhe de um serviço numa delegação específica",
        parameters=[
            OpenApiParameter('tipoPreco', str, description="ASSOCIADO ou NAO_ASSOCIADO para calcular precoAplicado"),
        ],
        responses={200: ServicoDelegacaoSerializer}
    )
    def get(self, request, *args, **kwargs):
        """Retorna os dados de uma configuração serviço ↔ delegação com preços.
        Requer perfil OPERADOR ou superior."""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Atualizar preços e disponibilidade de um serviço numa delegação",
        request=ServicoDelegacaoSerializer,
        responses={200: ServicoDelegacaoSerializer}
    )
    def put(self, request, *args, **kwargs):
        """Atualiza preços, percentual de entrada e disponibilidade.
        Requer perfil GESTOR ou superior."""
        return super().put(request, *args, **kwargs)
