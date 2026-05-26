from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


PERFIS = [
    ('OPERADOR', 'Operador'),
    ('GESTOR', 'Gestor'),
    ('FINANCEIRO', 'Financeiro'),
    ('DIRECAO', 'Direção'),
    ('ADMINISTRADOR', 'Administrador'),
]


class CredencialManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Credencial(AbstractBaseUser):
    # usuarioId é o ID do utilizador no usuario-service — passa a ser a PK desta tabela.
    # Desta forma o simplejwt consegue fazer OutstandingToken.user_id = usuarioId (UUID)
    # sem conflito, pois o FK aponta para esta PK e não para auth.User (inteiro).
    usuarioId   = models.UUIDField(primary_key=True)
    delegacaoId = models.UUIDField()
    email       = models.EmailField(unique=True)
    # 'password' e 'last_login' são fornecidos pelo AbstractBaseUser
    perfil      = models.CharField(max_length=20, choices=PERFIS)
    ativo       = models.BooleanField(default=True)
    createdAt   = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    objects = CredencialManager()

    @property
    def is_active(self):
        return self.ativo

    class Meta:
        db_table = 'credenciais'

    def __str__(self):
        return f'{self.email} ({self.perfil})'
