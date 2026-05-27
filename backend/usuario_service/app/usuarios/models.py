from django.db import models
import uuid

# Create your models here.

class Usuario(models.Model):
    

    PERFIS = [
        ('OPERADOR', 'Operador'),
        ('GESTOR', 'Gestor de Delegação'),
        ('FINANCEIRO', 'Financeiro'),
        ('DIRECAO', 'Direção'),
        ('ADMINISTRADOR', 'Administrador')
    ]

    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    passwordHash = models.CharField(max_length=255)
    perfil = models.CharField(choices=PERFIS)
    delegacaoId = models.UUIDField(null=True)
    ativo = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)


class Delegacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, auto_created=True, editable=False)
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=255)
    localizacao = models.CharField(max_length=255)
    responsavelId = models.UUIDField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)

