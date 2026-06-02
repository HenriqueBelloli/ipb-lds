from decimal import Decimal
from rest_framework import serializers
from .models import OrdemServico, OrdemServicoServico, OrdemServicoHistorico


class OrdemServicoServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdemServicoServico
        fields = [
            'id', 'servicoId', 'servicoDelegacaoId', 'precoAplicado',
            'percentualEntrada', 'bonificado', 'createdAt',
        ]
        read_only_fields = ['id', 'createdAt']


class OrdemServicoSerializer(serializers.ModelSerializer):
    itens = OrdemServicoServicoSerializer(many=True, read_only=True)

    class Meta:
        model = OrdemServico
        fields = [
            'id', 'clienteId', 'delegacaoContratacaoId', 'delegacaoExecucaoId',
            'usuarioCriacaoId', 'status', 'valorTotal', 'tipoPreco',
            'motivoCancelamento', 'createdAt', 'updatedAt', 'itens',
        ]
        read_only_fields = [
            'id', 'usuarioCriacaoId', 'delegacaoContratacaoId',
            'status', 'valorTotal', 'createdAt', 'updatedAt',
        ]


class OrdemServicoItemCreateSerializer(serializers.Serializer):
    servicoId = serializers.UUIDField()
    servicoDelegacaoId = serializers.UUIDField()
    precoAplicado = serializers.DecimalField(max_digits=10, decimal_places=2)
    percentualEntrada = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0'),
        max_value=Decimal('100'),
        default=Decimal('0.00'),
        required=False,
    )
    bonificado = serializers.BooleanField(default=False)


class OrdemServicoCreateSerializer(serializers.Serializer):
    clienteId = serializers.UUIDField()
    delegacaoExecucaoId = serializers.UUIDField()
    tipoPreco = serializers.ChoiceField(choices=['ASSOCIADO', 'NAO_ASSOCIADO'])
    itens = OrdemServicoItemCreateSerializer(many=True)

    def validate_itens(self, value):
        if not value:
            raise serializers.ValidationError('A OS deve ter pelo menos um item.')
        return value

    def create(self, validated_data):
        from django.db import transaction
        itens_data = validated_data.pop('itens')

        valor_total = sum(
            item['precoAplicado']
            for item in itens_data
            if not item.get('bonificado', False)
        ) or Decimal('0.00')
        with transaction.atomic():
            os = OrdemServico.objects.create(
                **validated_data,
                valorTotal=valor_total,
            )
            for item in itens_data:
                OrdemServicoServico.objects.create(ordemServicoId=os, **item)

        return os


class OrdemServicoHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdemServicoHistorico
        fields = ['id', 'usuarioId', 'statusAnterior', 'statusNovo', 'observacao', 'createdAt']
        read_only_fields = ['id', 'createdAt']
