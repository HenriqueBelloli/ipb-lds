"""
Management command: seed
Cria credenciais iniciais de teste se ainda não existirem.

UUIDs fixos — devem ser usados também no seed do usuario-service
para manter consistência entre os dois serviços.

Delegações:
  Bragança:   10000000-0000-0000-0000-000000000001
  Mirandela:  10000000-0000-0000-0000-000000000002

Utilizadores:
  ADMINISTRADOR:     20000000-0000-0000-0000-000000000001
  GESTOR:            20000000-0000-0000-0000-000000000002
  OPERADOR:          20000000-0000-0000-0000-000000000003
  FINANCEIRO:        20000000-0000-0000-0000-000000000004
  DIRECAO:           20000000-0000-0000-0000-000000000005
"""

from django.core.management.base import BaseCommand
from authentication.models import Credencial

# ── UUIDs fixos partilhados com o usuario-service ────────────────────────────

DELEGACAO_BRAGANCA  = '10000000-0000-0000-0000-000000000001'
DELEGACAO_MIRANDELA = '10000000-0000-0000-0000-000000000002'

SEED_DATA = [
    {
        'usuarioId':   '20000000-0000-0000-0000-000000000001',
        'delegacaoId': DELEGACAO_BRAGANCA,
        'email':       'admin@ldsgrupo1.pt',
        'password':    'Admin123!',
        'perfil':      'ADMINISTRADOR',
    },
    {
        'usuarioId':   '20000000-0000-0000-0000-000000000002',
        'delegacaoId': DELEGACAO_BRAGANCA,
        'email':       'gestor@ldsgrupo1.pt',
        'password':    'Gestor123!',
        'perfil':      'GESTOR',
    },
    {
        'usuarioId':   '20000000-0000-0000-0000-000000000003',
        'delegacaoId': DELEGACAO_MIRANDELA,
        'email':       'operador@ldsgrupo1.pt',
        'password':    'Operador123!',
        'perfil':      'OPERADOR',
    },
    {
        'usuarioId':   '20000000-0000-0000-0000-000000000004',
        'delegacaoId': DELEGACAO_BRAGANCA,
        'email':       'financeiro@ldsgrupo1.pt',
        'password':    'Financeiro123!',
        'perfil':      'FINANCEIRO',
    },
    {
        'usuarioId':   '20000000-0000-0000-0000-000000000005',
        'delegacaoId': DELEGACAO_BRAGANCA,
        'email':       'direcao@ldsgrupo1.pt',
        'password':    'Direcao123!',
        'perfil':      'DIRECAO',
    },
]


class Command(BaseCommand):
    help = 'Cria credenciais iniciais de teste (idempotente)'

    def handle(self, *args, **options):
        criados = 0
        ignorados = 0

        for dados in SEED_DATA:
            existe = Credencial.objects.filter(email=dados['email']).exists()
            if existe:
                ignorados += 1
                continue

            cred = Credencial(
                usuarioId=dados['usuarioId'],
                delegacaoId=dados['delegacaoId'],
                email=dados['email'],
                perfil=dados['perfil'],
                ativo=True,
            )
            cred.set_password(dados['password'])
            cred.save()
            criados += 1
            self.stdout.write(
                self.style.SUCCESS(f"  [+] {dados['perfil']:15s} {dados['email']}")
            )

        if criados:
            self.stdout.write(
                self.style.SUCCESS(f'\nSeed concluído: {criados} credencial(ais) criada(s).')
            )
        else:
            self.stdout.write(f'Seed: {ignorados} credencial(ais) já existente(s), nada a fazer.')
