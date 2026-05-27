import os
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class OrdensConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ordens'

    def ready(self):
        if os.environ.get('RUN_CONSUMER', 'True') == 'True':
            try:
                from .consumers import iniciar_consumers
                iniciar_consumers()
                logger.info('Consumer RabbitMQ do os-service iniciado')
            except Exception as e:
                logger.error(f'Erro ao iniciar consumer: {str(e)}')
