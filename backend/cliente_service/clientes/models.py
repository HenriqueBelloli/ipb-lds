from uuid import uuid4
from django.db import models


class Cliente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField( blank=True, null=True)
    morada = models.CharField(max_length=500, null=True, blank=True)
    flagAssociado = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    nif = models.CharField(max_length=20, unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        db_table = 'clientes'

    def __str__(self):
        return f'{self.nome} ({self.nif})'


class ClienteDelegacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4,editable=False)
    clienteId = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='clienteId', related_name='delegacoes')
    delegacaoId = models.UUIDField() # refencia externa sem ForeignKey
    createdAt = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'cliente_delegacoes'
        unique_together = ['clienteId', 'delegacaoId']
        ordering = ['-createdAt']


    def __str__(self):
        return f'Cliente {self.cliente_id} -> Delegação {self.delegacaoId}'
