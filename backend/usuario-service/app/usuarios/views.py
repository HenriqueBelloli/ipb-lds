from django.shortcuts import render
from rest_framework import generics
from .serializers import UsuarioSerializer, UsuarioCreateSerializer
from .models import Usuario

# Create your views here.

class UsuarioListCreateView(generics.ListCreateAPIView):
    permission_classes = ['IsAuthenticated', 'IsAdministrator']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UsuarioCreateSerializer
        
        return UsuarioSerializer
    
    def get_queryset(self):
        queryset = Usuario.objects.all()
        nome = self.request.query_params.get('nome')
        perfil = self.request.query_params.get('perfil')
        delegacaoId = self.request.query_params.get('delegacaoId')
        ativo = self.request.query_params.get('ativo')

        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        
        if perfil:
            queryset = queryset.filter(perfil = perfil)
        
        if delegacaoId:
            queryset = queryset.filter(delegacaoId = delegacaoId)

        if ativo is not None:
            queryset = queryset.filter(ativo = ativo.lower() == 'true')
        
        return queryset