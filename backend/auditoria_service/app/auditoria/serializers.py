from rest_framework import serializers
from .models import LogAuditoria


class LogAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogAuditoria
        fields = ['id', 'evento', 'servico', 'usuarioId',
                  'delegacaoId', 'payload', 'timestamp']
        read_only_fields = fields  # todos os campos são só leitura
