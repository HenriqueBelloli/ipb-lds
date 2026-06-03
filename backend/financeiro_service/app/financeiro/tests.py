from decimal import Decimal
from uuid import uuid4

from django.test import TestCase

from .consumers import handle_os_aprovada
from .models import ContaReceber


class GeracaoEntradaOSTests(TestCase):
    def test_gera_entrada_somando_percentual_por_item(self):
        os_id = uuid4()
        cliente_id = uuid4()

        handle_os_aprovada({
            'osId': str(os_id),
            'clienteId': str(cliente_id),
            'statusResultante': 'PAGAMENTO_PENDENTE',
            'valorTotal': '25.00',
            'itens': [
                {
                    'precoAplicado': '10.00',
                    'percentualEntrada': '0.00',
                    'bonificado': False,
                },
                {
                    'precoAplicado': '15.00',
                    'percentualEntrada': '10.00',
                    'bonificado': False,
                },
            ],
        })

        conta = ContaReceber.objects.get(ordemServicoId=os_id, tipo='ENTRADA')
        self.assertEqual(conta.clienteId, cliente_id)
        self.assertEqual(conta.valor, Decimal('1.50'))
        self.assertEqual(conta.status, 'ABERTA')

    def test_ignora_item_bonificado_no_calculo_da_entrada(self):
        os_id = uuid4()

        handle_os_aprovada({
            'osId': str(os_id),
            'clienteId': str(uuid4()),
            'statusResultante': 'PAGAMENTO_PENDENTE',
            'valorTotal': '25.00',
            'itens': [
                {
                    'precoAplicado': '15.00',
                    'percentualEntrada': '10.00',
                    'bonificado': True,
                },
            ],
        })

        self.assertFalse(ContaReceber.objects.filter(ordemServicoId=os_id).exists())

    def test_nao_duplica_entrada_para_mesma_os(self):
        os_id = uuid4()
        evento = {
            'osId': str(os_id),
            'clienteId': str(uuid4()),
            'statusResultante': 'PAGAMENTO_PENDENTE',
            'valorTotal': '15.00',
            'itens': [
                {
                    'precoAplicado': '15.00',
                    'percentualEntrada': '10.00',
                    'bonificado': False,
                },
            ],
        }

        handle_os_aprovada(evento)
        handle_os_aprovada(evento)

        self.assertEqual(ContaReceber.objects.filter(ordemServicoId=os_id, tipo='ENTRADA').count(), 1)
