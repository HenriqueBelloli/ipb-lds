import os
import logging
import requests

logger = logging.getLogger(__name__)

SERVICO_SERVICE_URL = os.environ.get('SERVICO_SERVICE_URL', 'http://servico-service:8004')


class ServicoServiceClient:

    @staticmethod
    def get_servicos_delegacao(delegacao_id: str, tipo_preco: str, token: str) -> list:
        try:
            r = requests.get(
                f'{SERVICO_SERVICE_URL}/api/servicos/delegacao/{delegacao_id}/'
                f'?tipoPreco={tipo_preco}&ativo=true',
                headers={'Authorization': f'Bearer {token}'},
                timeout=5,
            )
            r.raise_for_status()
            data = r.json()
            return data.get('results', data)
        except requests.exceptions.RequestException as e:
            raise Exception(f'servico-service indisponível: {str(e)}')
