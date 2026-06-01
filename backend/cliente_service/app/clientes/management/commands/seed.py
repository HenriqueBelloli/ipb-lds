"""
Management command: seed
Cria clientes iniciais de teste se ainda não existirem.

UUIDs fixos — os clientes são vinculados às delegações do usuario_service.

Clientes:
  Cliente Associado Demo:     30000000-0000-0000-0000-000000000001
  Cliente Não Associado Demo: 30000000-0000-0000-0000-000000000002

Delegações (UUIDs fixos do usuario_service):
  Sede:            10000000-0000-0000-0000-000000000001
  Delegação Norte: 10000000-0000-0000-0000-000000000002
"""

from django.core.management.base import BaseCommand

from clientes.models import Cliente, ClienteDelegacao

DELEGACAO_SEDE  = '10000000-0000-0000-0000-000000000001'
DELEGACAO_NORTE = '10000000-0000-0000-0000-000000000002'

CLIENTES_DATA = [
    {
        'id':            '30000000-0000-0000-0000-000000000001',
        'nif':           '123456789',
        'nome':          'Cliente Associado Demo',
        'telefone':      '910000001',
        'email':         'associado@demo.pt',
        'flagAssociado': True,
        'ativo':         True,
        'delegacoes':    [DELEGACAO_SEDE, DELEGACAO_NORTE],
    },
    {
        'id':            '30000000-0000-0000-0000-000000000002',
        'nif':           '987654321',
        'nome':          'Cliente Não Associado Demo',
        'telefone':      '910000002',
        'email':         'naosociado@demo.pt',
        'flagAssociado': False,
        'ativo':         True,
        'delegacoes':    [DELEGACAO_NORTE],
    },
]


class Command(BaseCommand):
    help = 'Cria clientes iniciais de teste (idempotente)'

    def handle(self, *args, **options):
        self._seed_clientes()

    def _seed_clientes(self):
        criados = 0
        ignorados = 0

        for dados in CLIENTES_DATA:
            pk = dados['id']
            delegacoes = dados['delegacoes']
            defaults = {k: v for k, v in dados.items() if k not in ('id', 'delegacoes')}

            cliente, created = Cliente.objects.get_or_create(id=pk, defaults=defaults)

            if created:
                criados += 1
                self.stdout.write(self.style.SUCCESS(f"  [+] {dados['nome']}"))
            else:
                ignorados += 1

            for delegacao_id in delegacoes:
                ClienteDelegacao.objects.get_or_create(
                    clienteId=cliente,
                    delegacaoId=delegacao_id,
                )

        if criados:
            self.stdout.write(self.style.SUCCESS(f'\nClientes: {criados} criado(s).'))
        else:
            self.stdout.write(f'Clientes: {ignorados} já existente(s), nada a fazer.')
