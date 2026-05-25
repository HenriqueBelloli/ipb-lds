from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notificacao
from .serializers import *
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

# Create your views here.

class NotificationListView(APIView):

    @extend_schema(
            operation_id="listar_notificacoes",
            request=None,
            responses={
                200: NotificationListSerializer
            }
    )
    def get(self, request):
        qs = Notificacao.objects.all()

        lida = request.query_params.get('lida')
        canal = request.query_params.get('canal')
        tipoDestinatario = request.query_params.get('tipoDestinatario')
        destinatarioId = request.query_params.get('destinatarioId')
        evento = request.query_params.get('evento')

        if lida:
            qs = qs.filter(lida = lida)
        
        if canal:
            qs = qs.filter(canal = canal)
        
        if tipoDestinatario:
            qs = qs.filter(tipoDestinatario = tipoDestinatario)
        
        if destinatarioId:
            qs = qs.filter(destinatarioId = destinatarioId)
        
        if evento:
            qs = qs.filter(evento = evento)
        
        serializer = NotificationListSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class NotificationDetailView(APIView):

    def _get_object(self, id):
        return get_object_or_404(Notificacao,id=id)


    @extend_schema(
            operation_id="detalhar_notificacao",
            request=None,
            responses={
                200: NotificationListSerializer,
                404: NotificationDetailErrorSerializer
            }
    )
    def get(self, request, id):

        notificacao = self._get_object(id=id)

        serializer = NotificationListSerializer(notificacao, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)


