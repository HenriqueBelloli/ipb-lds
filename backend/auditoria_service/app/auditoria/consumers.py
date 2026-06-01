import json
import logging
from shared.rabbitmq import start_consumer
from .models import LogAuditoria

logger = logging.getLogger(__name__)

EVENTOS_SUBSCRITOS = [
    'auth.login.success',
    'auth.login.failed',
    'usuario.criado',
    'usuario.atualizado',
    'usuario.desativado',
    'cliente.criado',
    'cliente.atualizado',
    'os.criada',
    'os.aprovada',
    'os.concluida',
    'os.cancelada',
    'os.status.atualizado',
    'financeiro.pagamento.entrada.confirmado',
    'financeiro.conta.paga',
    'financeiro.mensalidades.geradas',
    'conciliacao.automatica.concluida',
    'conciliacao.manual.realizada',
]


def processar_evento(ch, method, properties, body):
    """
    Handler único para todos os eventos.
    Grava o payload completo sem transformação.
    Nunca deve lançar exceção — log de erro e continua.
    """
    try:
        data = json.loads(body)
        routing_key = method.routing_key

        LogAuditoria.objects.create(
            evento=routing_key,
            servico=data.get('servico', 'desconhecido'),
            usuarioId=data.get('usuarioId') or data.get('usuarioCriacaoId'),
            delegacaoId=data.get('delegacaoId'),
            payload=data
        )
    except Exception as e:
        logger.error(
            f'[auditoria-service] Erro ao gravar evento '
            f'{method.routing_key}: {str(e)}'
        )


def iniciar_consumers():
    start_consumer(
        queue_name='auditoria_service_queue',
        routing_keys=EVENTOS_SUBSCRITOS,
        callback=processar_evento
    )
