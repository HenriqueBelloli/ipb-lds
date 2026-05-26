from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import LogAuditoria
from .serializers import LogAuditoriaSerializer
# Create your views here.

from shared.auth_middleware.permissions import IsAdministrador


class LogAuditoriaListView(generics.ListAPIView):
    serializer_class = LogAuditoriaSerializer
    permission_classes = [IsAuthenticated, IsAdministrador]

    def get_queryset(self):
        queryset = LogAuditoria.objects.all()
        evento = self.request.query_params.get('evento')
        servico = self.request.query_params.get('servico')
        usuario_id = self.request.query_params.get('usuarioId')
        delegacao_id = self.request.query_params.get('delegacaoId')
        data_inicio = self.request.query_params.get('dataInicio')
        data_fim = self.request.query_params.get('dataFim')

        if evento:
            queryset = queryset.filter(evento=evento)
        if servico:
            queryset = queryset.filter(servico=servico)
        if usuario_id:
            queryset = queryset.filter(usuarioId=usuario_id)
        if delegacao_id:
            queryset = queryset.filter(delegacaoId=delegacao_id)
        if data_inicio:
            queryset = queryset.filter(timestamp__date__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(timestamp__date__lte=data_fim)

        return queryset


class LogAuditoriaDetailView(generics.RetrieveAPIView):
    serializer_class = LogAuditoriaSerializer
    permission_classes = [IsAuthenticated, IsAdministrador]
    queryset = LogAuditoria.objects.all()

