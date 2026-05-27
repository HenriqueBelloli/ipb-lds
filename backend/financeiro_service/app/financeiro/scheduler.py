import os
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from .services.mensalidade_service import MensalidadeService

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    internal_secret = os.environ.get('INTERNAL_SERVICE_SECRET', '')

    scheduler.add_jobstore(DjangoJobStore(), 'default')
    scheduler.add_job(
        lambda: MensalidadeService.gerar_mensalidades(internal_secret=internal_secret),
        trigger = 'cron',
        day = 1,
        hour = 1,
        minute = 0,
        id = 'gerar_mensalidades_mensais',
        replace_existing = True
    )

    scheduler.start()