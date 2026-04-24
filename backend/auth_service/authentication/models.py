import uuid
from django.db import models


PERFIS = [
    ('OPERADOR', 'Operador'),
    ('GESTOR', 'Gestor'),
    ('FINANCEIRO', 'Financeiro'),
    ('DIRECAO', 'Direção'),
    ('ADMINISTRADOR', 'Administrador'),
]


class Credencial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuarioId = models.UUIDField(unique=True)
    delegacaoId = models.UUIDField()
    email = models.EmailField(unique=True)
    passwordHash = models.CharField(max_length=255)
    perfil = models.CharField(max_length=20, choices=PERFIS)
    ativo = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'credenciais'

    def __str__(self):
        return f'{self.email} ({self.perfil})'
