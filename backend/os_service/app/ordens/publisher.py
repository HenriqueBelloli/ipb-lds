import logging
from shared.rabbitmq import publish_event as _publish

logger = logging.getLogger(__name__)


def publish_event(routing_key: str, data: dict):
    try:
        _publish(routing_key, data)
    except Exception as e:
        logger.error(f'Erro ao publicar evento {routing_key}: {str(e)}')
