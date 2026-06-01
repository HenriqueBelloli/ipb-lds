from django.apps import AppConfig



class FinanceiroConfig(AppConfig):
    name = 'financeiro'

    def ready(self):
        import sys

        #Não levantar o scheduler durante migracoes
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return

        from .scheduler import iniciar_scheduler
        from .consumers import iniciar_consumers
        iniciar_scheduler()
        iniciar_consumers()
