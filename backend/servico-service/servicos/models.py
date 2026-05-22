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

    def __str__(self):
        return self.nome
    
class ServicoDelegacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    servicoId = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='delegacoes')
    delegacaoId = models.UUIDField() # Referencia externa (apenas o UUID, não gera FK física)
    precoAssociado = models.DecimalField(max_digits=10, decimal_places=2)
    precoNaoAssociado = models.DecimalField(max_digits=10, decimal_places=2)
    percentualEntrada = models.DecimalField(max_digits=5,
                                            decimal_places=2,
                                            default=0,
                                            validators=[validar_percentual_entrada])
    ativo = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['servicoId', 'delegacaoId']

    def __str__(self):
        return f'{self.servicoId.nome} - Delegação {self.delegacaoId}'

