# servicos/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
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


class ServicoDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ServicoSerializer
    queryset = Servico.objects.all()

    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsAdministrador()]
        return [IsOperador()]


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
