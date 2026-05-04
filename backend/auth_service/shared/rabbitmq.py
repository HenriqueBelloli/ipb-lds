import pika
import json
import os
import logging
import threading

logger = logging.getLogger(__name__)


def publish_event(routing_key: str, data: dict):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.environ.get('RABBITMQ_HOST', 'rabbitmq'),
                port=int(os.environ.get('RABBITMQ_PORT', 5672)),
                credentials=pika.PlainCredentials(
                    os.environ.get('RABBITMQ_USER', 'guest'),
                    os.environ.get('RABBITMQ_PASS', 'guest')
                )
            )
        )
        channel = connection.channel()
        channel.exchange_declare(exchange='erp_events', exchange_type='topic', durable=True)
        channel.basic_publish(
            exchange='erp_events',
            routing_key=routing_key,
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        logger.info(f'Evento publicado: {routing_key}')
    except Exception as e:
        logger.error(f'Erro ao publicar evento {routing_key}: {str(e)}')


def start_consumer(queue_name: str, routing_keys: list, callback):
    def consume():
        import traceback
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=os.environ.get('RABBITMQ_HOST', 'rabbitmq'),
                    port=int(os.environ.get('RABBITMQ_PORT', 5672)),
                    credentials=pika.PlainCredentials(
                        os.environ.get('RABBITMQ_USER', 'guest'),
                        os.environ.get('RABBITMQ_PASS', 'guest')
                    ),
                    connection_attempts=3,
                    retry_delay=2
                )
            )
            channel = connection.channel()
            channel.exchange_declare(exchange='erp_events', exchange_type='topic', durable=True)
            channel.queue_declare(queue=queue_name, durable=True)

            for key in routing_keys:
                channel.queue_bind(exchange='erp_events', queue=queue_name, routing_key=key)

            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            logger.info(f'Consumidor iniciado: {queue_name} com routing keys {routing_keys}')
            channel.start_consuming()
        except Exception as e:
            logger.error(f'Erro no consumer {queue_name}: {str(e)}', exc_info=True)
            import time
            time.sleep(5)
            consume()

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
