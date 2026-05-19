import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class FinanceiroServiceClient:
    BASE_URL = settings.FINANCEIRO_SERVICE_URL
    @staticmethod
    def verificar_inadimplente(cliente_id: str, token: str) -> bool:
        """
        gggggggg
        """
        url, f'{FinanceiroServiceClient.BASE_URL}/api/financeiro/clientes/{cliente_id}/inadimplente/'
        try:
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'},
                timeout=5,
            )
            if response.status_code == 200:
                return response.json().get('inadimplente', False)
            return False
        except requests.exceptions.Timeout:
            logger.warning('Timeou ao contactar financeiro-service para cliente %s.', cliente_id)
            return False
        except requests.exceptions.RequestException as exc:
            logger.error('Erro de rede ao contactar financeiro-service: %', exc)
            return False