from rest_framework import serializers
from .models import Cliente, ClienteDelegacao


class ClienteDelegacaoSerializer(serializers.ModelsSerializer):
    class Meta:
        model = ClienteDelegacao
        fields = ['id', 'clienteId', 'createdAt']
        read_only_fields = ['id', 'createdAt']


class ClienteSerializer(serializers.ModelSerializer):
    delegacoes = ClienteDelegacaoSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'telefone', 'email', 'morada', 'flaAssociado', 'ativo', 'createdAt', 'delegacoes', 'nif']
        read_only_fields = ['id', 'createdAt']
    
class ClienteDetalheSerializer(ClienteSerializer):
    inadimplente = serializers.BooleanField(read_only=True, allow_null=True, default=None)
    divida_total = serializers.FloatField(read_only=True,allow_null=True, default=None)

    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ['inadimplente', 'divida_total']

class AssociaDelegacaoSerializer(serializers.Serializer):
    delegacaoId = serializers.UUIDField()

    def validate_delegacaoId(self, value):
        return value
