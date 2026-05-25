from rest_framework import serializers
from .models import Notificacao

class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao

        fields = [
            'id',
            'destinatarioId',
            'tipoDestinatario',
            'canal',
            'titulo',
            'mensagem',
            'evento',
            'payload',
            'enviado',
            'lida',
            'erro',
            'createdAt'
        ]

        read_only_fields = [
            'id',
            'createdAt'
        ]