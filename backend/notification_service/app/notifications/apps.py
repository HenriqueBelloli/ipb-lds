from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        import sys
        if "migrate" in sys.argv:
            return
        
        from .consumers import iniciar_consumers
        iniciar_consumers()
