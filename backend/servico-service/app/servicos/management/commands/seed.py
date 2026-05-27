"""
Management command: seed
Cria serviços e associações a delegações iniciais de teste se ainda não existirem.

UUIDs fixos — devem ser usados também nos seeds dos outros serviços
para manter consistência entre os serviços.

Delegações:
  Sede:              10000000-0000-0000-0000-000000000001
  Delegação Norte:   10000000-0000-0000-0000-000000000002

Serviços:
  Consulta Médica:   30000000-0000-0000-0000-000000000001
  Fisioterapia:      30000000-0000-0000-0000-000000000002
  Análises Clínicas: 30000000-0000-0000-0000-000000000003
"""

from django.core.management.base import BaseCommand
from servicos.models import Servico, ServicoDelegacao

# ── UUIDs fixos partilhados com os restantes serviços ────────────────────────
DELEGACAO_SEDE  = '10000000-0000-0000-0000-000000000001'
DELEGACAO_NORTE = '10000000-0000-0000-0000-000000000002'

# ── Dados base dos serviços ───────────────────────────────────────────────────
SERVICOS_DATA = [
    {
        'id':             '30000000-0000-0000-0000-000000000001',
        'nome':           'Medição',
        'descricao':      'Medição de área de terreno..',
        'flagBonificavel': True,
        'ativo':          True,
    },
    {
        'id':             '30000000-0000-0000-0000-000000000002',
        'nome':           'Carteira de motorista',
        'descricao':      'Aulas para adquirir a licença para dirigir trator.',
        'flagBonificavel': False,
        'ativo':          True,
    },
    {
        'id':             '30000000-0000-0000-0000-000000000003',
        'nome':           'Análises Clínicas',
        'descricao':      'Colheitas e análises laboratoriais.',
        'flagBonificavel': False,
        'ativo':          True,
    },
]

# ── Associações serviço ↔ delegação ──────────────────────────────────────────
# precoAssociado    → preço para utentes associados
# precoNaoAssociado → preço para utentes não associados
# percentualEntrada → percentual de entrada (0–100)
SERVICOS_DELEGACOES_DATA = [
    {
        'servicoId':          '30000000-0000-0000-0000-000000000001',
        'delegacaoId':        DELEGACAO_SEDE,
        'precoAssociado':     '25.00',
        'precoNaoAssociado':  '45.00',
        'percentualEntrada':  '20.00',
        'ativo':              True,
    },
    {
        'servicoId':          '30000000-0000-0000-0000-000000000001',
        'delegacaoId':        DELEGACAO_NORTE,
        'precoAssociado':     '22.00',
        'precoNaoAssociado':  '40.00',
        'percentualEntrada':  '20.00',
        'ativo':              True,
    },
    {
        'servicoId':          '30000000-0000-0000-0000-000000000002',
        'delegacaoId':        DELEGACAO_SEDE,
        'precoAssociado':     '15.00',
        'precoNaoAssociado':  '30.00',
        'percentualEntrada':  '10.00',
        'ativo':              True,
    },
    {
        'servicoId':          '30000000-0000-0000-0000-000000000002',
        'delegacaoId':        DELEGACAO_NORTE,
        'precoAssociado':     '13.00',
        'precoNaoAssociado':  '28.00',
        'percentualEntrada':  '10.00',
        'ativo':              True,
    },
    {
        'servicoId':          '30000000-0000-0000-0000-000000000003',
        'delegacaoId':        DELEGACAO_SEDE,
        'precoAssociado':     '10.00',
        'precoNaoAssociado':  '20.00',
        'percentualEntrada':  '0.00',
        'ativo':              True,
    },
]


class Command(BaseCommand):
    help = 'Cria serviços e associações a delegações iniciais de teste (idempotente)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n── Serviços ──────────────────────────────────────'))
        servicos_criados   = 0
        servicos_ignorados = 0

        for dados in SERVICOS_DATA:
            if Servico.objects.filter(id=dados['id']).exists():
                servicos_ignorados += 1
                continue

            Servico.objects.create(
                id=dados['id'],
                nome=dados['nome'],
                descricao=dados['descricao'],
                flagBonificavel=dados['flagBonificavel'],
                ativo=dados['ativo'],
            )
            servicos_criados += 1
            self.stdout.write(
                self.style.SUCCESS(f"  [+] {dados['nome']}")
            )

        if servicos_criados:
            self.stdout.write(
                self.style.SUCCESS(f'\n  Serviços: {servicos_criados} criado(s).')
            )
        else:
            self.stdout.write(f'  Serviços: {servicos_ignorados} já existente(s), nada a fazer.')

        # ── ServicoDelegacao ──────────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('\n── Associações Serviço ↔ Delegação ───────────────'))
        assoc_criadas   = 0
        assoc_ignoradas = 0

        for dados in SERVICOS_DELEGACOES_DATA:
            servico = Servico.objects.get(id=dados['servicoId'])

            ja_existe = ServicoDelegacao.objects.filter(
                servicoId=servico,
                delegacaoId=dados['delegacaoId'],
            ).exists()

            if ja_existe:
                assoc_ignoradas += 1
                continue

            ServicoDelegacao.objects.create(
                servicoId=servico,
                delegacaoId=dados['delegacaoId'],
                precoAssociado=dados['precoAssociado'],
                precoNaoAssociado=dados['precoNaoAssociado'],
                percentualEntrada=dados['percentualEntrada'],
                ativo=dados['ativo'],
            )
            assoc_criadas += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [+] {servico.nome:25s} → delegação {dados['delegacaoId']}"
                )
            )

        if assoc_criadas:
            self.stdout.write(
                self.style.SUCCESS(f'\n  Associações: {assoc_criadas} criada(s).')
            )
        else:
            self.stdout.write(f'  Associações: {assoc_ignoradas} já existente(s), nada a fazer.')

        self.stdout.write(self.style.SUCCESS('\nSeed concluído.\n'))