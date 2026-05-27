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

class NotificationDetailErrorSerializer(serializers.Serializer):
    message = serializers.CharField()

class NotificacaoMarkAsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao

        fields = [
            'lida'
        ]

class NotificacaoMarkAsReadErrorSerializer(serializers.Serializer):
    message = serializers.CharField()

class NotificationMarkAllAsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao

        fields = [
            'id',
            'lida'
        ]

        read_only_fields = ['id']