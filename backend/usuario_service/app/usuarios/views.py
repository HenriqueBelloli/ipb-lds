from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework import status
from .serializers import *
from .models import Usuario, Delegacao
from .publishers import publish_usuario_criado, publish_usuario_desativado

# Create your views here.

PERFIL_ORDER = {
    'OPERADOR': 1,
    'GESTOR': 2,
    'FINANCEIRO': 3,
    'DIRECAO': 4,
    'ADMINISTRADOR': 5
}

def has_minimum_perfil(user_perfil, required_perfil):
    return PERFIL_ORDER.get(user_perfil, 0) >= PERFIL_ORDER.get(required_perfil, 99)


class IsAdministrator(BasePermission):
    message = "Acesso restrito a administradores"

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and has_minimum_perfil(request.user.perfil, 'ADMINISTRADOR')
        )

class IsAnyPerfil(BasePermission):
    message = "Autenticação necessária."

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
        )

class UsuarioListCreateView(APIView):
    #GET /api/usuarios/ - Listar utilizadores com filtros (Admin)
    #POST /api/usuarios/ - Criar utilizador (Admin)

    #permission_classes = [IsAdministrator]
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        usuario = serializer.save()
        publish_usuario_criado(usuario)
        

    def get(self, request):
        qs = Usuario.objects.all()

        perfil = request.query_params.get('perfil')
        ativo = request.query_params.get('ativo')
        delegecao_id = request.query_params.get('delegacaoId')
        nome = request.query_params.get('nome')
        email = request.query_params.get('email')

        if perfil:
            qs = qs.filter(perfil = perfil)
        
        if ativo is not None:
            qs = qs.filter(ativo = ativo.lower() in ('true', '1', 'yes'))
        
        if delegecao_id:
            qs = qs.filter(delegacaoId = delegecao_id)
        
        if nome:
            qs = qs.filter(nome__icontains = nome)

        if email:
            qs = qs.filter(email__icontains = email)
        
        serializer = UsuarioListSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = UsuarioCreateSerializer(data = request.data)

        if serializer.is_valid():
            self.perform_create(serializer)

            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    

class UsuarioDetailUpdateView(APIView):
    #GET /api/usuarios/{id}/ Detalhe de usuario (Admin)
    #PUT /api/usuarios/{id}/ Atualizar utilizador (Admin)

    #permission_classes = [IsAdministrator]
    permission_classes = [AllowAny]

    def perform_update(self, serializer, pk):
        usuario_anterior = self._get_object(pk)
        usuario = serializer.save()

        #publicar o evento se foi desativado
        if usuario_anterior.ativo and not usuario.ativo:
            publish_usuario_desativado(usuario)

    def _get_object(self, pk):
        return get_object_or_404(Usuario, pk = pk)
    
    def get(self, request, pk):
        usuario = self._get_object(pk)
        serializer = UsuarioListSerializer(usuario)

        return Response(serializer.data, status = status.HTTP_200_OK)
    
    def put(self, request, pk):
        usuario = self._get_object(pk)
        serializer = UsuarioUpdateSerializer(usuario, data = request.data, partial = True)
        if serializer.is_valid():
            self.perform_update(serializer, pk)
            
            return Response(UsuarioListSerializer(usuario).data, status = status.HTTP_200_OK)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class DelegacaoListCreateView(APIView):
    #GET /api/delegacoes - Listar delegações ativas (qualquer perfil)
    #POST /api/delegacoes - Criar delegacao (Admin)

    # def get_permissions(self):
    #     if self.request.method == 'GET':
            
    #         return [IsAnyPerfil()]
        
    #     return [IsAdministrator()]

    permission_classes = [AllowAny]
    
    def get(self, request):
        qs = Delegacao.objects.filter(ativo = True)

        nome = request.query_params.get('nome')
        codigo = request.query_params.get('codigo')
        localizacao = request.query_params.get('localizacao')

        if nome:
            qs = qs.filter(nome__icontains = nome)
        
        if codigo:
            qs = qs.filter(codigo__icontains = codigo)
        
        if localizacao:
            qs = qs.filter(localizacao__icontains = localizacao)
        
        serializer = DelegacaoListSerializer(qs, many = True)

        return Response(serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request):
        serializer = DelegacaoCreateSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    

class DelegacaoUpdateView(APIView):
    #PUT /api/delegacoes/{id} - Atualizar delegacao (inclui campo ativo) (Admin)

    #permission_classes = [IsAdministrator]
    permission_classes = [AllowAny]

    def put(self, request, pk):
        delegacao = get_object_or_404(Delegacao, pk = pk)

        serializer = DelegacaoUpdateSerializer(delegacao, data = request.data, partial = True)

        if serializer.is_valid():
            serializer.save()

            return Response(DelegacaoListSerializer(delegacao).data, status = status.HTTP_200_OK)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
