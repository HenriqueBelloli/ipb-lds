from rest_framework import serializers
from .models import Cliente, ClienteDelegacao


class ClienteDelegacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteDelegacao
        fields = ['id', 'clienteId', 'delegacaoId', 'createdAt']
        read_only_fields = ['id', 'createdAt']


class ClienteSerializer(serializers.ModelSerializer):
    delegacoes = ClienteDelegacaoSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = ['id', 'nif', 'nome', 'telefone', 'email', 'morada', 'flagAssociado', 'ativo', 'createdAt']
    
class ClienteDetalheSerializer(ClienteSerializer):
    inadimplente = serializers.BooleanField(read_only=True, allow_null=True, default=None)
    tipoPreco = serializers.SerializerMethodField(read_only=True, allow_null=True, default=None)

    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ['inadimplente', 'divida_total']

class AssociarDelegacaoSerializer(serializers.Serializer):
    delegacaoId = serializers.UUIDField()

    def validate_delegacaoId(self, value):
        return value
