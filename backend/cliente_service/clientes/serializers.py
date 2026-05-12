from rest_framework import serializers
from .models import Cliente, Delegacao

class DelegacaoSerializer(serializers.ModelsSerializer):
    class Meta:
        model = Delegacao
        field = ['id', 'delegacao_id', 'nome']

class ClienteSerializer(serializers.ModelSerializer):
    delegacoes = DelegacaoSerializer(many=True, read_only=True)
    delegacao_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Delegacao.objects.all(),
        source='delegacoes',
        write_only=True,
        required=False
    )
    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'email', 'telefone', 'nif', 'delegacoes', 'delegacao_ids', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ClienteDetalheSerializer(ClienteSerializer):
    """
    Usando apenas no endpoint de detalhe (retrieve).
    Enriquecido com dados do financeiro-service.
    A lógica de inadimplencia é EXCLUSIVA do financeiro-service.
    """
    inadimplente = serializers.BooleanField(read_only=True, default=None, allow_null=True)
    divida_total = serializers.FloatField(read_only=True, default=None, allow_null=True)

    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ['inadimplente', 'divida_total']

class AssociarDelegacaoSerializer(serializers.Serializer):
    """
    Usando no endpoint de associação de delegação.
    """
    delegacao_id = serializers.IntegerField()