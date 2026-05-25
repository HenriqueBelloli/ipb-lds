from django.apps import AppConfig
from .scheduler import iniciar_scheduler
from .consumers import iniciar_consumers


class FinanceiroConfig(AppConfig):
    name = 'financeiro'

    def ready(self):
        iniciar_scheduler()
        iniciar_consumers()
