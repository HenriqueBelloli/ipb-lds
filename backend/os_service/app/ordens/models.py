import uuid
from django.db import models

STATUS_CHOICES = [
    ('ORCAMENTO', 'Orçamento'),
    ('AGUARDA_APROVACAO', 'Aguarda Aprovação'),
    ('PAGAMENTO_PENDENTE', 'Pagamento Pendente'),
    ('A_EXECUTAR', 'A Executar'),
    ('EM_EXECUCAO', 'Em Execução'),
    ('CONCLUIDO', 'Concluído'),
    ('FATURADO', 'Faturado'),
    ('CANCELADO', 'Cancelado'),
]

TIPO_PRECO_CHOICES = [
    ('ASSOCIADO', 'Associado'),
    ('NAO_ASSOCIADO', 'Não Associado'),
]


class OrdemServico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clienteId = models.UUIDField()
    delegacaoContratacaoId = models.UUIDField()
    delegacaoExecucaoId = models.UUIDField()
    usuarioCriacaoId = models.UUIDField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ORCAMENTO')
    valorTotal = models.DecimalField(max_digits=10, decimal_places=2)
    tipoPreco = models.CharField(max_length=20, choices=TIPO_PRECO_CHOICES)
    motivoCancelamento = models.TextField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ordem_servico'
        ordering = ['-createdAt']


class OrdemServicoServico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordemServicoId = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name='itens',
        db_column='ordemServicoId',
    )
    servicoId = models.UUIDField()
    servicoDelegacaoId = models.UUIDField()
    precoAplicado = models.DecimalField(max_digits=10, decimal_places=2)
    bonificado = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ordem_servico_servico'


class OrdemServicoHistorico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordemServicoId = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name='historico',
        db_column='ordemServicoId',
    )
    usuarioId = models.UUIDField(null=True, blank=True)
    statusAnterior = models.CharField(max_length=30, null=True, blank=True)
    statusNovo = models.CharField(max_length=30)
    observacao = models.TextField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ordem_servico_historico'
        ordering = ['createdAt']
