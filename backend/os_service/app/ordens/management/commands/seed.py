import uuid
from django.core.management.base import BaseCommand
from ordens.models import OrdemServico, OrdemServicoServico, OrdemServicoHistorico

DELEGACAO_BRAGANCA_ID = uuid.UUID('10000000-0000-0000-0000-000000000001')
DELEGACAO_MIRANDELA_ID = uuid.UUID('10000000-0000-0000-0000-000000000002')

USUARIO_GESTOR_ID = uuid.UUID('20000000-0000-0000-0000-000000000002')
USUARIO_OPERADOR_ID = uuid.UUID('20000000-0000-0000-0000-000000000003')

CLIENTE_ID = uuid.UUID('30000000-0000-0000-0000-000000000001')
# Medição (servico-service: 30000000-...-0001) @ Bragança (servico-delegacao: 40000000-...-0001)
SERVICO_ID = uuid.UUID('30000000-0000-0000-0000-000000000001')
SERVICO_DELEGACAO_ID = uuid.UUID('40000000-0000-0000-0000-000000000001')

OS_ID = uuid.UUID('50000000-0000-0000-0000-000000000001')


class Command(BaseCommand):
    help = 'Seed de dados de desenvolvimento para o os-service'

    def handle(self, *args, **options):
        if OrdemServico.objects.filter(id=OS_ID).exists():
            self.stdout.write('Seed já aplicado — a ignorar.')
            return

        os = OrdemServico.objects.create(
            id=OS_ID,
            clienteId=CLIENTE_ID,
            delegacaoContratacaoId=DELEGACAO_BRAGANCA_ID,
            delegacaoExecucaoId=DELEGACAO_BRAGANCA_ID,
            usuarioCriacaoId=USUARIO_OPERADOR_ID,
            status='ORCAMENTO',
            valorTotal='150.00',
            tipoPreco='ASSOCIADO',
        )

        OrdemServicoServico.objects.create(
            ordemServicoId=os,
            servicoId=SERVICO_ID,
            servicoDelegacaoId=SERVICO_DELEGACAO_ID,
            precoAplicado='150.00',
            bonificado=False,
        )

        OrdemServicoHistorico.objects.create(
            ordemServicoId=os,
            usuarioId=USUARIO_OPERADOR_ID,
            statusAnterior=None,
            statusNovo='ORCAMENTO',
            observacao='OS criada (seed)',
        )

        self.stdout.write(self.style.SUCCESS(f'OS de desenvolvimento criada: {OS_ID}'))
