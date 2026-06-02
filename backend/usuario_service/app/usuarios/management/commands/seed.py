"""
Management command: seed
Cria delegações e utilizadores iniciais de teste se ainda não existirem.

UUIDs fixos — partilhados com o auth-service para manter consistência.

Delegações:
  Bragança:              10000000-0000-0000-0000-000000000001
  Mirandela:             10000000-0000-0000-0000-000000000002
  Braga:                 10000000-0000-0000-0000-000000000003
  Macedo de Cavaleiros:  10000000-0000-0000-0000-000000000004
  Vinhais:               10000000-0000-0000-0000-000000000005
  Mogadouro:             10000000-0000-0000-0000-000000000006
  Miranda do Douro:      10000000-0000-0000-0000-000000000007

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

DELEGACAO_BRAGANCA  = '10000000-0000-0000-0000-000000000001'
DELEGACAO_MIRANDELA = '10000000-0000-0000-0000-000000000002'
DELEGACAO_BRAGA     = '10000000-0000-0000-0000-000000000003'
DELEGACAO_MACEDO    = '10000000-0000-0000-0000-000000000004'
DELEGACAO_VINHAIS   = '10000000-0000-0000-0000-000000000005'
DELEGACAO_MOGADOURO = '10000000-0000-0000-0000-000000000006'
DELEGACAO_MIRANDA   = '10000000-0000-0000-0000-000000000007'

USUARIO_ADMIN    = '20000000-0000-0000-0000-000000000001'
USUARIO_OPERADOR = '20000000-0000-0000-0000-000000000003'

DELEGACOES_DATA = [
    {
        'id':            DELEGACAO_BRAGANCA,
        'codigo':        'BRAGANCA',
        'nome':          'Delegação Bragança',
        'localizacao':   'Bragança',
        'responsavelId': USUARIO_ADMIN,
    },
    {
        'id':            DELEGACAO_MIRANDELA,
        'codigo':        'MIRANDELA',
        'nome':          'Delegação Mirandela',
        'localizacao':   'Mirandela',
        'responsavelId': USUARIO_OPERADOR,
    },
    {
        'id':            DELEGACAO_BRAGA,
        'codigo':        'BRAGA',
        'nome':          'Delegação Braga',
        'localizacao':   'Braga',
        'responsavelId': None,
    },
    {
        'id':            DELEGACAO_MACEDO,
        'codigo':        'MACEDO',
        'nome':          'Delegação Macedo de Cavaleiros',
        'localizacao':   'Macedo de Cavaleiros',
        'responsavelId': None,
    },
    {
        'id':            DELEGACAO_VINHAIS,
        'codigo':        'VINHAIS',
        'nome':          'Delegação Vinhais',
        'localizacao':   'Vinhais',
        'responsavelId': None,
    },
    {
        'id':            DELEGACAO_MOGADOURO,
        'codigo':        'MOGADOURO',
        'nome':          'Delegação Mogadouro',
        'localizacao':   'Mogadouro',
        'responsavelId': None,
    },
    {
        'id':            DELEGACAO_MIRANDA,
        'codigo':        'MIRANDA',
        'nome':          'Delegação Miranda do Douro',
        'localizacao':   'Miranda do Douro',
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
        'delegacaoId': DELEGACAO_BRAGANCA,
    },
    {
        'id':          '20000000-0000-0000-0000-000000000002',
        'nome':        'Gestor',
        'email':       'gestor@ldsgrupo1.pt',
        'password':    'Gestor123!',
        'perfil':      'GESTOR',
        'delegacaoId': DELEGACAO_BRAGANCA,
    },
    {
        'id':          USUARIO_OPERADOR,
        'nome':        'Operador',
        'email':       'operador@ldsgrupo1.pt',
        'password':    'Operador123!',
        'perfil':      'OPERADOR',
        'delegacaoId': DELEGACAO_MIRANDELA,
    },
    {
        'id':          '20000000-0000-0000-0000-000000000004',
        'nome':        'Financeiro',
        'email':       'financeiro@ldsgrupo1.pt',
        'password':    'Financeiro123!',
        'perfil':      'FINANCEIRO',
        'delegacaoId': DELEGACAO_BRAGANCA,
    },
    {
        'id':          '20000000-0000-0000-0000-000000000005',
        'nome':        'Direção',
        'email':       'direcao@ldsgrupo1.pt',
        'password':    'Direcao123!',
        'perfil':      'DIRECAO',
        'delegacaoId': DELEGACAO_BRAGANCA,
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
