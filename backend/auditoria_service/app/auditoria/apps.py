from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class AuditoriaConfig(AppConfig):
    name = 'auditoria'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import os
        if os.environ.get('RUN_CONSUMER', 'True') == 'True':
            try:
                from .consumers import iniciar_consumers
                iniciar_consumers()
                logger.info('Consumer RabbitMQ iniciado')

            except Exception as e:
                logger.error(f"Erro ao iniciar consumer: {str(e)}")