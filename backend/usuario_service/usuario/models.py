from django.db import models
from django.utils import timezone
# Create your models here.

class Usuario(models.Model):
    class Perfil(models.TextChoices):
        OPERADOR = 'O', 'Operador de delegacao'
        GESTOR = 'G', 'Gestor de delegacao'
        FINANCEIRO = 'F', 'Financeiro'
        DIRECAO = 'D', 'Direcao'
        ADMIN = 'A', 'Administrador do sistema'


    id = models.UUIDField(auto_created=True, null=False, primary_key=True)

    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    passwordHash = models.CharField(max_length=255)
    perfil = models.CharField(
        max_length=1,
        choices=Perfil.choices,
        default=Perfil.OPERADOR
    )
    delegacaoId = models.IntegerField()
    ativo = models.BooleanField(default=True)
    createdAt = models.DateTimeField(default=timezone.now())


    
