from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from services.mensalidade_service import MensalidadeService

def iniciar_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_jobstore(DjangoJobStore(), 'default')
    scheduler.add_job(
        MensalidadeService.gerar_mensalidades,
        trigger = 'cron',
        day = 1,
        hour = 1,
        minute = 0,
        id = 'gerar_mensalidades_mensais',
        replace_existing = True
    )

    scheduler.start()