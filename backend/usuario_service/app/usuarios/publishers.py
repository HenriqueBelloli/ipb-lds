import json
import os
import pika
from .models import Usuario

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
            content_type='application/json',
        ),

    )

    connection.close()


def publish_usuario_criado(usuario : Usuario):
    publish(
        exchange='usuarios',
        routing_key='usuario.criado',
        body={
            'id': str(usuario.id),
            'nome': usuario.nome,
            'email': usuario.email,
            'perfil': usuario.perfil,
            'delegacaoId': str(usuario.delegacaoId) if usuario.delegacaoId else None,
            'ativo': usuario.ativo
        }
    )

def publish_usuario_desativado(usuario: Usuario):
    publish(
        exchange='usuarios',
        routing_key='usuario.desativado',
        body={
            'id': str(usuario.id),
            'nome': usuario.nome,
            'email': usuario.email
        }
    )