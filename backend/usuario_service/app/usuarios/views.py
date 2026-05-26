from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Usuario, Delegacao
from .publishers import publish_usuario_criado, publish_usuario_desativado
from drf_spectacular.utils import extend_schema
from shared.auth_middleware.permissions import IsOperador, IsAdministrador


class UsuarioListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOperador()]
        return [IsAdministrador()]

    def perform_create(self, serializer):
        usuario = serializer.save()
        publish_usuario_criado(usuario)

    @extend_schema(responses=UsuarioListSerializer(many=True))
    def get(self, request):
        qs = Usuario.objects.all()

        perfil = request.query_params.get('perfil')
        ativo = request.query_params.get('ativo')
        delegecao_id = request.query_params.get('delegacaoId')
        nome = request.query_params.get('nome')
        email = request.query_params.get('email')

        if perfil:
            qs = qs.filter(perfil=perfil)

        if ativo is not None:
            qs = qs.filter(ativo=ativo.lower() in ('true', '1', 'yes'))

        if delegecao_id:
            qs = qs.filter(delegacaoId=delegecao_id)

        if nome:
            qs = qs.filter(nome__icontains=nome)

        if email:
            qs = qs.filter(email__icontains=email)

        serializer = UsuarioListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=UsuarioCreateSerializer, responses=UsuarioCreateSerializer)
    def post(self, request):
        serializer = UsuarioCreateSerializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioDetailUpdateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOperador()]
        return [IsAdministrador()]

    def perform_update(self, serializer, pk):
        usuario_anterior = self._get_object(pk)
        usuario = serializer.save()

        if usuario_anterior.ativo and not usuario.ativo:
            publish_usuario_desativado(usuario)

    def _get_object(self, pk):
        return get_object_or_404(Usuario, pk=pk)

    @extend_schema(responses=UsuarioListSerializer(many=False))
    def get(self, request, pk):
        usuario = self._get_object(pk)
        serializer = UsuarioListSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=UsuarioUpdateSerializer, responses=UsuarioListSerializer(many=False))
    def put(self, request, pk):
        usuario = self._get_object(pk)
        serializer = UsuarioUpdateSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer, pk)
            return Response(UsuarioListSerializer(usuario).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DelegacaoListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOperador()]
        return [IsAdministrador()]

    @extend_schema(responses=DelegacaoListSerializer(many=True))
    def get(self, request):
        qs = Delegacao.objects.filter(ativo=True)

        nome = request.query_params.get('nome')
        codigo = request.query_params.get('codigo')
        localizacao = request.query_params.get('localizacao')

        if nome:
            qs = qs.filter(nome__icontains=nome)

        if codigo:
            qs = qs.filter(codigo__icontains=codigo)

        if localizacao:
            qs = qs.filter(localizacao__icontains=localizacao)

        serializer = DelegacaoListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=DelegacaoCreateSerializer, responses=DelegacaoCreateSerializer)
    def post(self, request):
        serializer = DelegacaoCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DelegacaoUpdateView(APIView):
    permission_classes = [IsAdministrador]

    @extend_schema(request=DelegacaoUpdateSerializer, responses=DelegacaoListSerializer(many=False))
    def put(self, request, pk):
        delegacao = get_object_or_404(Delegacao, pk=pk)

        serializer = DelegacaoUpdateSerializer(delegacao, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(DelegacaoListSerializer(delegacao).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok"})
