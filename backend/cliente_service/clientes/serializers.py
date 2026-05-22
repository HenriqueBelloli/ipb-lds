from rest_framework import serializers
from .models import Cliente, ClienteDelegacao


class ClienteDelegacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteDelegacao
        fields = ['id', 'clienteId', 'delegacaoId', 'createdAt']
        read_only_fields = ['id', 'createdAt']


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nif', 'nome', 'telefone', 'email',
                  'morada', 'flagAssociado', 'ativo', 'createdAt']
        read_only_fields = ['id', 'createdAt']


class ClienteDetalheSerializer(ClienteSerializer):
    inadimplente = serializers.SerializerMethodField()
    tipoPreco = serializers.SerializerMethodField()

    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ['inadimplente', 'tipoPreco']
# os campos que vão ser atualizados para o cliente!
   
    def get_inadimplente(self, obj):
        return self.context.get('inadimplente', False)

    def get_tipoPreco(self, obj):
        inadimplente = self.context.get('inadimplente', False)
        if obj.flagAssociado and not inadimplente:
            return 'ASSOCIADO'
        return 'NAO_ASSOCIADO'


class AssociarDelegacaoSerializer(serializers.Serializer):
    delegacaoId = serializers.UUIDField()

    def validate_delegacaoId(self, value):
        return value