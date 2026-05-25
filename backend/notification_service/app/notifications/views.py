from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notificacao
from .serializers import *

# Create your views here.

class NotificationListView(APIView):

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

