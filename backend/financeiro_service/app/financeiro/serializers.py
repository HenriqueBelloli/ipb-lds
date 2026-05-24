from .models import *
from rest_framework import serializers

class ContasReceberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaReceber

        fields = [
            'id',
            'clienteId',
            'ordemServicoId',
            'tipo',
            'valor',
            'valorPago',
            'status',
            'dataVencimento',
            'createdAt'
        ]

        read_only_fields = [
            'id', 
            'createdAt'
        ]

class ContasReceberDetailErrorSerializer(serializers.Serializer):
    message = serializers.CharField()

class ContasReceberErrorFaturarSerializer(serializers.Serializer):
    message = serializers.CharField()

class ContasReceberFaturarInputSerializer(serializers.Serializer):
    pk = serializers.UUIDField()

class ClienteInadimplenteSerializer(serializers.Serializer):
    inadimplente = serializers.BooleanField()

class PagamentoConfirmadoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento

        fields = [
            'id',
            'contaReceberId',
            'usuarioId',
            'valor',
            'data',
            'referenciaBancaria',
            'createdAt'
        ]

        read_only_fields = [
            'id',
            'createdAt'
        ]

class PagamentoViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento

        fields = [
            'id',
            'contaReceberId',
            'usuarioId',
            'valor',
            'data',
            'referenciaBancaria',
            'createdAt'
        ]

        read_only_fields = [
            'id',
            'createdAt'
        ]

class PagamentoDetailErrorSerializer(serializers.Serializer):
    message = serializers.CharField()

class RegistrarPagamentoErrorSerializer(serializers.Serializer):
    message = serializers.CharField()

class VerificarEntradaPagaSerializer(serializers.Serializer):
    entrada_paga = serializers.BooleanField()

class MensalidadeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoFinanceira

        fields = [
            'id',
            'chave',
            'valor',
            'atualizadoEm',
            'usuarioId'
        ]

        read_only_fields = [
            'id',
            'atualizadoEm',
            'usuarioId'
        ]

class MensalidadePutErrorSerializer(serializers.Serializer):
    message = serializers.CharField()

class MensalidadeViewEntrySerializer(serializers.Serializer):
    valor = serializers.FloatField()
    usuarioId = serializers.UUIDField()

class GerarMensalidadesSerializer(serializers.Serializer):
    geradas = serializers.IntegerField()
    ignoradas = serializers.IntegerField()

class GerarMensalidadesErrorSerializer(serializers.Serializer):
    message = serializers.CharField()