from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

    def ready(self):
        import os
        if os.environ.get('RUN_CONSUMER', 'True') == 'True':
            try:
                from .consumers import start_auth_consumer
                start_auth_consumer()
                logger.info('Consumer RabbitMQ iniciado')
            except Exception as e:
                logger.error(f'Erro ao iniciar consumer: {str(e)}')
