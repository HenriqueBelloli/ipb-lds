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


class ClienteDetailSerializer(serializers.ModelSerializer):
    inadimplente = serializers.SerializerMethodField()
    tipoPreco = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = ['id', 'nif', 'nome', 'telefone', 'email', 'morada',
                  'flagAssociado', 'ativo', 'createdAt',
                  'inadimplente', 'tipoPreco']
        read_only_fields = ['id', 'createdAt']

    def get_inadimplente(self, obj):
        return self.context.get('inadimplente', False)

    def get_tipoPreco(self, obj):
        inadimplente = self.context.get('inadimplente', False)
        if obj.flagAssociado and not inadimplente:
            return 'ASSOCIADO'
        return 'NAO_ASSOCIADO'
