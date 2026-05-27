import json
import logging
from shared.rabbitmq import start_consumer

logger = logging.getLogger(__name__)


def handle_pagamento_entrada_confirmado(data: dict):
    from django.db import transaction
    from .models import OrdemServico, OrdemServicoHistorico
    from .publisher import publish_event

    os_id = data.get('osId')
    try:
        with transaction.atomic():
            os = OrdemServico.objects.select_for_update().get(
                id=os_id,
                status='PAGAMENTO_PENDENTE',
            )
            status_anterior = os.status
            os.status = 'A_EXECUTAR'
            os.save()

            OrdemServicoHistorico.objects.create(
                ordemServicoId=os,
                usuarioId=None,
                statusAnterior=status_anterior,
                statusNovo='A_EXECUTAR',
                observacao='Entrada confirmada automaticamente via evento financeiro',
            )

            publish_event('os.status.atualizado', {
                'servico': 'os-service',
                'osId': str(os.id),
                'statusAnterior': status_anterior,
                'statusNovo': 'A_EXECUTAR',
                'automatico': True,
            })

    except OrdemServico.DoesNotExist:
        logger.warning(f'OS {os_id} não encontrada ou não está em PAGAMENTO_PENDENTE')
    except Exception as e:
        logger.error(f'Erro ao processar financeiro.pagamento.entrada.confirmado: {str(e)}')


def processar_evento(ch, method, properties, body):
    try:
        data = json.loads(body)
        routing_key = method.routing_key
        handlers = {
            'financeiro.pagamento.entrada.confirmado': handle_pagamento_entrada_confirmado,
        }
        handler = handlers.get(routing_key)
        if handler:
            handler(data)
    except Exception as e:
        logger.error(f'Erro ao processar evento {method.routing_key}: {str(e)}')


def iniciar_consumers():
    start_consumer(
        'os_service_queue',
        ['financeiro.pagamento.entrada.confirmado'],
        processar_evento,
    )
