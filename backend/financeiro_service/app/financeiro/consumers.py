from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from .models import ContaReceber
import json
import pika
import logging
import time
import threading

logger = logging.getLogger(__name__)

def handle_os_aprovada(data):
    os_id = data.get('osId')
    cliente_id = data.get('clienteId')
    itens = data.get('itens', [])
    valor_total = Decimal(data.get('valorTotal', '0'))
    status_resultante = data.get('statusResultante')

    #Só gera entrada se OS foi para PAGAMENTO_PENDENTE
    if status_resultante != 'PAGAMENTO_PENDENTE':
        return
    
    #Calcular valor da entrada
    #percentualEntrada vem nos itens - usar o maior percentual
    #ou a média

    percentual = max(
        item.get('percentualEntrada', 0) for item in itens
    ) if itens else 0

    if percentual <= 0:
        return
    
    valor_entrada = (valor_total * Decimal(percentual)) / Decimal(100)
    data_vencimento = timezone.now().date() + timedelta(days=3)

    ContaReceber.objects.create(
        clienteId = cliente_id,
        ordemServicoId = os_id,
        tipo = 'ENTRADA',
        valor = valor_entrada,
        status = 'ABERTA',
        dataVencimento = data_vencimento
    )

def handle_os_concluida(data):
    #os.concluida apenas registra
    #faturacao é manual pelo Financeiro
    pass

def dispatch_event(
        ch,
        method,
        properties,
        body
):
    
    data = json.loads(body)
    routing_key = method.routing_key
    handlers = {
        'os.aprovada': handle_os_aprovada,
        'os.concluida': handle_os_concluida,
    }

    handler = handlers.get(routing_key)
    if handler:
        handler(data=data)

def start_consumer(
        queue_name,
        routing_keys,
        callback,
        exchange = "events",
        exchange_type = "topic",
        host = "rabbitmq",
        port = 5672,
        virtual_host = "/",
        username = "guest",
        password = "guest",
        reconnect_delay = 5,
        run_in_thread = True
):
    
    def _consume():
        while True:
            try:
                credentials = pika.PlainCredentials(username, password)
                parameters = pika.ConnectionParameters(
                    host=host,
                    port=port,
                    virtual_host=virtual_host,
                    credentials=credentials,
                    heartbeat=60,
                    blocked_connection_timeout=300
                )

                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()

                channel.exchange_declare(
                    exchange=exchange,
                    exchange_type=exchange_type,
                    durable=True
                )

                channel.queue_declare(queue=queue_name, durable=True)

                for key in routing_keys:
                    channel.queue_bind(
                        exchange=exchange,
                        queue=queue_name,
                        routing_key=key
                    )

                channel.basic_qos(prefetch_count=1)

                def on_message(ch, method, properties, body):
                    try:
                        callback(ch, method, properties, body)
                        ch.basic_ack(delivery_tag = method.delivery_tag)
                    
                    except Exception as e:
                        logger.error(f"Erro ao processar mensagem: {e}")
                        #recoloca na fila (requeue = false manda pra dead-letter)
                        ch.basic_nack(delivery_tag = method.delivery_tag, requeue = False)

                
                channel.basic_consume(queue=queue_name, on_message_callback=on_message)

                logger.info(f"[{queue_name}] Aguardando mensagens...")
                channel.start_consuming()

            except (pika.exceptions.AMQPConnectionError, Exception) as e:
                logger.error(f"[{queue_name}] Conexão perdida: {e}. Reconectando em {reconnect_delay}s...")
                time.sleep(reconnect_delay)
            
    if run_in_thread:
        thread = threading.Thread(target=_consume, daemon=True, name=f"consumer-{queue_name}")
        thread.start()
        return thread
    else:
        _consume()

def iniciar_consumers():
    start_consumer(
        queue_name='financeiro_os_events',
        routing_keys = ['os.aprovada', 'os.concluida'],
        callback = dispatch_event
    )


