import os
import logging
import requests

logger = logging.getLogger(__name__)

FINANCEIRO_SERVICE_URL = os.environ.get('FINANCEIRO_SERVICE_URL', 'http://financeiro-service:8006')


class FinanceiroServiceClient:

    @staticmethod
    def verificar_entrada_paga(os_id: str, token: str) -> bool:
        try:
            r = requests.get(
                f'{FINANCEIRO_SERVICE_URL}/api/financeiro/contas-receber/entrada-paga/{os_id}/',
                headers={'Authorization': f'Bearer {token}'},
                timeout=5,
            )
            if r.status_code == 200:
                return r.json().get('paga', False)
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f'Erro ao verificar entrada paga: {str(e)}')
            raise Exception(f'financeiro-service indisponível: {str(e)}')

    @staticmethod
    def verificar_pagamentos_os(os_id: str, token: str) -> bool:
        try:
            r = requests.get(
                f'{FINANCEIRO_SERVICE_URL}/api/financeiro/pagamentos/os/{os_id}/',
                headers={'Authorization': f'Bearer {token}'},
                timeout=5,
            )
            if r.status_code == 200:
                return r.json().get('temPagamentos', False)
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f'Erro ao verificar pagamentos da OS: {str(e)}')
            return False
