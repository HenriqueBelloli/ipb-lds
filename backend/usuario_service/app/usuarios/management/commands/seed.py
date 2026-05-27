"""
Management command: seed
Cria delegações e utilizadores iniciais de teste se ainda não existirem.

UUIDs fixos — partilhados com o auth-service para manter consistência.

Delegações:
  Sede:              10000000-0000-0000-0000-000000000001
  Delegação Norte:   10000000-0000-0000-0000-000000000002
  Delegação Centro:  10000000-0000-0000-0000-000000000003
  Delegação Sul:     10000000-0000-0000-0000-000000000004
  Delegação Alentejo:10000000-0000-0000-0000-000000000005
  Delegação Algarve: 10000000-0000-0000-0000-000000000006
  Delegação Açores:  10000000-0000-0000-0000-000000000007
  Delegação Madeira: 10000000-0000-0000-0000-000000000008
  Delegação Beiras:  10000000-0000-0000-0000-000000000009

Utilizadores:
  ADMINISTRADOR:     20000000-0000-0000-0000-000000000001
  GESTOR:            20000000-0000-0000-0000-000000000002
  OPERADOR:          20000000-0000-0000-0000-000000000003
  FINANCEIRO:        20000000-0000-0000-0000-000000000004
  DIRECAO:           20000000-0000-0000-0000-000000000005
"""

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from usuarios.models import Delegacao, Usuario

# ── UUIDs fixos partilhados com o auth-service ───────────────────────────────

DELEGACAO_SEDE     = '10000000-0000-0000-0000-000000000001'
DELEGACAO_NORTE    = '10000000-0000-0000-0000-000000000002'
DELEGACAO_CENTRO   = '10000000-0000-0000-0000-000000000003'
DELEGACAO_SUL      = '10000000-0000-0000-0000-000000000004'
DELEGACAO_ALENTEJO = '10000000-0000-0000-0000-000000000005'
DELEGACAO_ALGARVE  = '10000000-0000-0000-0000-000000000006'
DELEGACAO_ACORES   = '10000000-0000-0000-0000-000000000007'
DELEGACAO_MADEIRA  = '10000000-0000-0000-0000-000000000008'
DELEGACAO_BEIRAS   = '10000000-0000-0000-0000-000000000009'

USUARIO_ADMIN      = '20000000-0000-0000-0000-000000000001'
USUARIO_OPERADOR   = '20000000-0000-0000-0000-000000000003'

DELEGACOES_DATA = [
    {
        'id':           DELEGACAO_SEDE,
        'codigo':       'SEDE',
        'nome':         'Sede Central',
        'localizacao':  'Lisboa',
        'responsavelId': USUARIO_ADMIN,
    },
    {
        'id':           DELEGACAO_NORTE,
        'codigo':       'NORTE',
        'nome':         'Delegação Norte',
        'localizacao':  'Porto',
        'responsavelId': USUARIO_OPERADOR,
    },
    {
        'id':           DELEGACAO_CENTRO,
        'codigo':       'CENTRO',
        'nome':         'Delegação Centro',
        'localizacao':  'Coimbra',
        'responsavelId': None,
    },
    {
        'id':           DELEGACAO_SUL,
        'codigo':       'SUL',
        'nome':         'Delegação Sul',
        'localizacao':  'Faro',
        'responsavelId': None,
    },
    {
        'id':           DELEGACAO_ALENTEJO,
        'codigo':       'ALENTEJO',
        'nome':         'Delegação Alentejo',
        'localizacao':  'Évora',
        'responsavelId': None,
    },
    {
        'id':           DELEGACAO_ALGARVE,
        'codigo':       'ALGARVE',
        'nome':         'Delegação Algarve',
        'localizacao':  'Lagos',
        'responsavelId': None,
    },
    {
        'id':           DELEGACAO_ACORES,
        'codigo':       'ACORES',
        'nome':         'Delegação Açores',
        'localizacao':  'Ponta Delgada',
        'responsavelId': None,
    },
    {
        'id':           DELEGACAO_MADEIRA,
        'codigo':       'MADEIRA',
        'nome':         'Delegação Madeira',
        'localizacao':  'Funchal',
        'responsavelId': None,
    },
    {
        'id':           DELEGACAO_BEIRAS,
        'codigo':       'BEIRAS',
        'nome':         'Delegação Beiras',
        'localizacao':  'Viseu',
        'responsavelId': None,
    },
]

USUARIOS_DATA = [
    {
        'id':          USUARIO_ADMIN,
        'nome':        'Administrador',
        'email':       'admin@ldsgrupo1.pt',
        'password':    'Admin123!',
        'perfil':      'ADMINISTRADOR',
        'delegacaoId': DELEGACAO_SEDE,
    },
    {
        'id':          '20000000-0000-0000-0000-000000000002',
        'nome':        'Gestor',
        'email':       'gestor@ldsgrupo1.pt',
        'password':    'Gestor123!',
        'perfil':      'GESTOR',
        'delegacaoId': DELEGACAO_SEDE,
    },
    {
        'id':          USUARIO_OPERADOR,
        'nome':        'Operador',
        'email':       'operador@ldsgrupo1.pt',
        'password':    'Operador123!',
        'perfil':      'OPERADOR',
        'delegacaoId': DELEGACAO_NORTE,
    },
    {
        'id':          '20000000-0000-0000-0000-000000000004',
        'nome':        'Financeiro',
        'email':       'financeiro@ldsgrupo1.pt',
        'password':    'Financeiro123!',
        'perfil':      'FINANCEIRO',
        'delegacaoId': DELEGACAO_SEDE,
    },
    {
        'id':          '20000000-0000-0000-0000-000000000005',
        'nome':        'Direção',
        'email':       'direcao@ldsgrupo1.pt',
        'password':    'Direcao123!',
        'perfil':      'DIRECAO',
        'delegacaoId': DELEGACAO_SEDE,
    },
]


class Command(BaseCommand):
    help = 'Cria delegações e utilizadores iniciais de teste (idempotente)'

    def handle(self, *args, **options):
        self._seed_delegacoes()
        self._seed_usuarios()

    def _seed_delegacoes(self):
        criadas = 0
        ignoradas = 0

        for dados in DELEGACOES_DATA:
            _, created = Delegacao.objects.get_or_create(
                id=dados['id'],
                defaults={
                    'codigo':        dados['codigo'],
                    'nome':          dados['nome'],
                    'localizacao':   dados['localizacao'],
                    'responsavelId': dados['responsavelId'],
                    'ativo':         True,
                },
            )
            if created:
                criadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  [+] DELEGACAO  {dados['codigo']:10s} {dados['nome']}")
                )
            else:
                ignoradas += 1

        if criadas:
            self.stdout.write(
                self.style.SUCCESS(f'\nDelegações: {criadas} criada(s).')
            )
        else:
            self.stdout.write(f'Delegações: {ignoradas} já existente(s), nada a fazer.')

    def _seed_usuarios(self):
        criados = 0
        ignorados = 0

        for dados in USUARIOS_DATA:
            _, created = Usuario.objects.get_or_create(
                id=dados['id'],
                defaults={
                    'nome':         dados['nome'],
                    'email':        dados['email'],
                    'passwordHash': make_password(dados['password']),
                    'perfil':       dados['perfil'],
                    'delegacaoId':  dados['delegacaoId'],
                    'ativo':        True,
                },
            )
            if created:
                criados += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  [+] {dados['perfil']:15s} {dados['email']}")
                )
            else:
                ignorados += 1

        if criados:
            self.stdout.write(
                self.style.SUCCESS(f'\nUtilizadores: {criados} criado(s).')
            )
        else:
            self.stdout.write(f'Utilizadores: {ignorados} já existente(s), nada a fazer.')
