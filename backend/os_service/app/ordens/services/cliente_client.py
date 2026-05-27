import os
import logging
import requests

logger = logging.getLogger(__name__)

CLIENTE_SERVICE_URL = os.environ.get('CLIENTE_SERVICE_URL', 'http://cliente-service:8003')


class ClienteServiceClient:

    @staticmethod
    def get_cliente(cliente_id: str, token: str) -> dict:
        try:
            r = requests.get(
                f'{CLIENTE_SERVICE_URL}/api/clientes/{cliente_id}/',
                headers={'Authorization': f'Bearer {token}'},
                timeout=5,
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'cliente-service indisponível: {str(e)}')
