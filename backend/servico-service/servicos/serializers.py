from rest_framework import serializers
from .models import Servico, ServicoDelegacao
from .validators import validar_precos, validar_percentual_entrada

class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = ['id', 'nome', 'descricao', 'flagBonificavel', 'ativo', 'createdAt']
        read_only_fields = ['id', 'createdAt']

class ServicoDelegacaoSerializer(serializers.ModelSerializer):
    nome = serializers.CharField('servicoId.nome', read_only=True)
    descricao = serializers.CharField(source='servicoId.descricao', read_only=True)
    flagBonificavel = serializers.BooleanField(source='servicoId.flagBonificavel', read_only=True)
    
    class Meta:
        model = ServicoDelegacao
        fields = ['id', 'servicoId', 'delegacaoId', 'nome', 'descricao', 'flagBonificavel', 'precoAssociado', 'precoNaoAssociado', 'precoAplicado', 'percentualEntrada', 'ativo', 'createcAt',]
        read_only_fields = ['id', 'createdAt']
    def get_preco_aplicado(self, obj):
        tipo_preco = self.context.get('tipoPreco')
        if tipo_preco == 'ASSOCIADO':
            return obj.precoAssociado
        if tipo_preco == 'NAO_ASSOCIADO':
            return obj.precoNaoAssociado
        return None
    
    def validate(self, data):
        validar_precos(
            data.get('precoAssociado', 0),
            data.get('precoNaoAssociado', 0),
        )
        validar_percentual_entrada(data.get('validar_percentual_entrada', 0)),
        return data