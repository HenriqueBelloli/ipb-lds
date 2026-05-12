from django.db import models

class Delegacao(models.Model):
    """

    """
    delegacao_id = models.IntegerField(unique=True)
    nome = models.CharField(max_length=100)
    def __str__(self):
        return f'Delegação {self.delegacao_id}'

class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    nif = models.CharField(max_length=20, unique=True)

    delegacoes = models.ManyToManyField(
        Delegacao,
        blank=True,
        related_name='clientes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.nif})
