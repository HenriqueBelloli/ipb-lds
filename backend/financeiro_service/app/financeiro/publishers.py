import json
import os
import pika

from .models import ContaReceber

def get_connection():
    credentials = pika.PlainCredentials(
        username=os.environ.get('RABBITMQ_USER', 'guest'),
        password=os.environ.get('RABBITMQ_PASS', 'guest')
    )

    parameters = pika.ConnectionParameters(
        host=os.environ.get('RABBITMQ_HOST', 'localhost'),
        port=int(os.environ.get('RABBITMQ_PORT', 5672)),
        credentials=credentials
    )

    return pika.BlockingConnection(parameters=parameters)

def publish(exchange, routing_key, body):
    connection = get_connection()

    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)

    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(body),
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type='application/json'
        ),
    )

    connection.close()


def publish_pagamento_confirmado(conta : ContaReceber):
    #o status vai vir sempre como PAGA

    if conta.tipo == 'ENTRADA':
        publish(
            exchange='erp_events',
            routing_key='financeiro.pagamento.entrada.confirmado',
            body={
                'servico': 'financeiro-service',
                'osId': str(conta.ordemServicoId),
                'contaReceberId': str(conta.id),
            }
        )
        return

    publish(
        exchange='erp_events',
        routing_key='financeiro.conta.paga',
        body={
            'servico': 'financeiro-service',
            'contaReceberId': str(conta.id),
            'clienteId': str(conta.clienteId),
            'tipo': conta.tipo,
        }
    )

    return 

def publish_mensalidades_geradas(mesReferencia, totalGeradas, totalIgnoradas):

    publish(
        exchange='erp_events',
        routing_key='financeiro.mensalidades.geradas',
        body={
            'servico': 'financeiro-service',
            'mesReferencia': mesReferencia,
            'totalGeradas': totalGeradas,
            'totalIgnoradas': totalIgnoradas,
        }
    )

