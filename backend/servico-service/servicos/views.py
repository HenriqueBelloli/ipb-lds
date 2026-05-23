from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
# from django.shortcuts import render
from .models import Servico, ServicoDelegacao
from .serializers import ServicoSerializer, ServicoDelegacaoSerializer
from shared.auth_middleware.permissions import IsAdministrador, IsGestor

class ServicoListCreateView(generics.ListAPIView):
    serializer_class = ServicoSerializer

    def get_permissions(self):
        if self.request.method == 'POST':

            return [IsAuthenticated(), IsAdministrador()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Servico.objects.all()
        params = self.request.query_params

        nome = params.get('nome')
        flag_bonificavel = params.get('flagBonificavel')
        ativo = params.get('ativo')

        if nome:
            queryset.filter(nome__icontains=nome)
        if flag_bonificavel is not None:
            queryset = queryset.filter(flagBonificavel=flag_bonificavel.lower() == 'true')
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo.lower() == 'true')

        return queryset.order_by('nome')

class SservicoDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ServicoSerializer
    queryset = Servico.objects.all()


    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsAuthenticated(), IsAdministrador()]
        return [IsAuthenticated()]

class ServicoDelegacaoListCreateView(generics.ListCreateAPIView):
    serializer_class = ServicoDelegacaoSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsGestor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        delegacao_id = self.kwargs.get('delegacaoId')
        queryset = ServicoDelegacao.objects.filter(
            delegacaoId=delegacao_id
        ).select_related('servicoId')

        ativo = self.request.query_params.get('ativo')
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo.lower() == 'true')

        return queryset.order_by('servicoId__nome')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tipoPreco'] = self.request.query_params.get('tipoPreco')
        return context


class ServicoDelegacaoDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ServicoDelegacaoSerializer
    queryset = ServicoDelegacao.objects.select_related('servicoId')

    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsAuthenticated(), IsGestor()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tipoPreco'] = self.request.query_params.get('tipoPreco')
        return context