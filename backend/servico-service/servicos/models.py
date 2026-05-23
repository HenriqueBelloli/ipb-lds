from django.db import models
import uuid
from .validators import validar_percentual_entrada

class Servico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    flagBonificavel = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'servicos'
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
class ServicoDelegacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    servicoId = models.ForeignKey(Servico, on_delete=models.CASCADE, db_column='servicoId', related_name='delegacoes')
    delegacaoId = models.UUIDField() # Referencia externa (apenas o UUID, não gera FK física)
    precoAssociado = models.DecimalField(max_digits=10, decimal_places=2)
    precoNaoAssociado = models.DecimalField(max_digits=10, decimal_places=2)
    percentualEntrada = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ativo = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'servicos_delegacoes'
        unique_together = ['servicoId__nome']

    def __str__(self):
        return f'{self.servicoId.nome} -> Delegação {self.delegacaoId}'