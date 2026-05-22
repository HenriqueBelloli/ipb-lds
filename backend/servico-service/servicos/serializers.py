from rest_framework import serializers
from .models import Servico, ServicoDelegacao
from .validators import validar_precos

class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = ['id', 'descricao', 'flagBonificavel', 'ativo', 'createdAt']
        read_only_fields = ['id', 'createdAt']
class ServicoDelegacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicoDelegacao
        fields = ['id', 'servicoId', 'precoAssociado', 'precoNaoAssociado', 'percentualEntrada', 'ativo', 'createdAt']
        read_only_fields = ['id', 'createdAt']
    def validate(self, data):
        preco_asc = data.get('precoAssociado', self.instance.precoAssociado if self.instance else 0)
        preco_nao_asc = data.get('precoNaoAssociado', self.instance.precoNaoAssociado if self.instance else 0)

        validar_precos(preco_asc, preco_nao_asc)
        return data
class ServicoPorDelegacaoResponseSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='servicoId.nome', read_only=True)
    descricao = serializers.CharField(source='servicoId.descricao', read_only=True)
    flagBonificavel = serializers.BooleanField(source='servicoId.flagBonificavel',read_only=True)
    precoAplicado = serializers.SerializerMethodField()
    class Meta:
        model = ServicoDelegacao
        fields = ['id', 'servicoId', 'delegacaoId', 'nome', 'descricao', 'flagBonificavel', 'precoAssociado', 'precoNaoAssociado', 'precoAplicado', 'percentualEntrada', 'ativo']
    def get_preco_aplicado(self, obj):
        tipo_preco = self.context.get('tipoPreco')
        if tipo_preco == 'ASSOCIADO':
            return obj.precoAssociado
        if tipo_preco == 'NAO_ASSOCIADO':
            return obj.precoNaoAssociado
        return None