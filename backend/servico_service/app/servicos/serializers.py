# servicos/serializers.py
from rest_framework import serializers
from .models import Servico, ServicoDelegacao


class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = ['id', 'nome', 'descricao', 'flagBonificavel',
                  'ativo', 'createdAt']
        read_only_fields = ['id', 'createdAt']


class ServicoDelegacaoSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='servicoId.nome', read_only=True)
    descricao = serializers.CharField(
        source='servicoId.descricao', read_only=True
    )
    flagBonificavel = serializers.BooleanField(
        source='servicoId.flagBonificavel', read_only=True
    )
    precoAplicado = serializers.SerializerMethodField()

    class Meta:
        model = ServicoDelegacao
        fields = ['id', 'servicoId', 'delegacaoId', 'nome', 'descricao',
                  'flagBonificavel', 'precoAssociado', 'precoNaoAssociado',
                  'precoAplicado', 'percentualEntrada', 'ativo', 'createdAt']
        read_only_fields = ['id', 'createdAt']

    def get_precoAplicado(self, obj):
        tipo_preco = self.context.get('tipoPreco')
        if tipo_preco == 'ASSOCIADO':
            return obj.precoAssociado
        if tipo_preco == 'NAO_ASSOCIADO':
            return obj.precoNaoAssociado
        return None

    def validate(self, data):
        preco_assoc = data.get('precoAssociado', 0)
        preco_nao = data.get('precoNaoAssociado', 0)
        percentual = data.get('percentualEntrada', 0)

        if preco_assoc <= 0:
            raise serializers.ValidationError(
                {'precoAssociado': 'Deve ser maior que zero.'}
            )
        if preco_nao <= 0:
            raise serializers.ValidationError(
                {'precoNaoAssociado': 'Deve ser maior que zero.'}
            )
        if preco_assoc > preco_nao:
            raise serializers.ValidationError(
                'precoAssociado não pode ser maior que precoNaoAssociado.'
            )
        if not (0 <= percentual <= 100):
            raise serializers.ValidationError(
                {'percentualEntrada': 'Deve estar entre 0 e 100.'}
            )
        return data
