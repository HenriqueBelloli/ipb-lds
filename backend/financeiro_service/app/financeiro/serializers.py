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
