mport httpx
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def obter_inadimplencia(cliente_id: int) -> dict | None:
    """
    Consulta o financeiro-service.
    A lógica de inadimplência é exclusiva desse serviço.
     Retorna None se indisponível (fail-open).
    """
    url = f'{settings.FINANCEIRO_SERVICE_URL}/inadimplencia/{cliente_id}'
    try:
        response = httpx.get(url, timeout=3.0)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        logger.warning(f'[financeiro-service] Timeout - cliente {cliente_id}')
        return None
    except Exception as e:
        logger.error(f'[financeiro-service] Erro: {e}')
        return None