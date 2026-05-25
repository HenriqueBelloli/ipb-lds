from .models import Notificacao
from .services.cliente_client import ClienteServiceClient
from .services.email_service import EmailService
import json
import pika
import logging
import threading
import time

logger = logging.getLogger(__name__)

def handle_os_aprovada(data):
    status_resultante = data.get('statusResultante')

    #Apenas notifica se foi para PAGAMENTO_PENDENTE
    if status_resultante != 'PAGAMENTO_PENDENTE':
        return
    
    #Notificacao interna para o financeiro
    Notificacao.objects.create(
        destinatarioId = None,
        tipoDestinatario = 'SISTEMA',
        canal = 'INTERNO',
        titulo = 'OS aguarda pagamento de entrada',
        mensagem = f"OS {data.get('osId')} aprovada e a aguardar pagamento de entrada no valor de {data.get('valorTotal')}",
        evento = 'os.aprovada',
        payload = data,
        enviado = True
    )

def handle_os_cancelada(data):
    os_id = data.get('osId')
    cliente_id = data.get('clienteId')
    motivo = data.get('motivo', 'nao especificado')

    #1. Notificacao interna para o sistema
    Notificacao.objects.create(
        destinatarioId = None,
        tipoDestinatario = 'SISTEMA',
        canal = 'INTERNO',
        titulo = 'Ordem de Serviço Cancelada',
        mensagem = f"A OS {os_id} foi cancelada. Motivo: {motivo}",
        evento = 'os.cancelada',
        payload = data,
        enviado = True
    )

    #2. Email ao cliente se tiver email registrado
    cliente  = ClienteServiceClient.get_cliente_anonimo(cliente_id)
    if cliente and cliente.get('email'):
        sucesso = EmailService.enviar(
            destinatario = cliente['email'],
            assunto = "A sua Ordem de Serviço foi cancelada",
            corpo = f"Informamos que a sua OS foi cancelada.\nMotivo: {motivo}\n\nPara mais informacoes contate a sua delegacao."
        )

        Notificacao.objects.create(
            destinatarioId = cliente_id,
            tipoDestinatario = 'CLIENTE',
            canal = 'EMAIL',
            titulo = 'OS Cancelada',
            mensagem = f"Email enviado ao cliente sobre cancelamento da OS {os_id}",
            evento = 'os.cancelada',
            paylaod = data,
            enviado = sucesso,
            erro = None if sucesso else 'Falha no envio de email'
        )

def handle_os_concluida(data):
    
    Notificacao.objects.create(
        destinatarioId = None,
        tipoDestinatario = 'SISTEMA',
        canal = 'Interno',
        titulo = 'OS concluida - aguarda faturacao',
        mensagem = f"A OS {data.get('osId')} foi concluida e esta a aguardar faturacao pelo modulo financeiro",
        evento = 'os.concluida',
        payload = data,
        enviado = True
    )

def handle_conta_paga(data):
    Notificacao.objects.create(
        destinatarioId = None,
        tipoDestinatario = 'SISTEMA',
        canal = 'INTERNO',
        titulo = 'Pagamento recebido',
        mensagem = f"Conta {data.get('contaReceberId')} tipo {data.get('tipo')} totalmente liquidada.",
        evento = 'financeiro.conta.paga',
        payload = data,
        enviado = True
    )

def handle_mensalidades_geradas(data):
    mes = data.get('mesReferencia')
    total = data.get('totalGeradas', 0)
    ignoradas = data.get('totalIgnoradas', 0)

    #Notificacao de sistema - resumo para o financeiro
    Notificacao.objects.create(
        destinatarioId = None,
        tipoDestinatario = 'SISTEMA',
        canal = 'INTERNO',
        titulo = "Mensalidades geradas automaticamente",
        mensagem = f"Geradas {total} mensalidades para {mes}. {ignoradas} ignoradas por ja existirem.",
        evento = 'financeiro.mensalidades.geradas',
        payload = data,
        enviado = True
    )

    #Poderia enviar email a cada associado mas requer consulta
    #ao cliente-service com a lista completa
    #implementar como melhoria futura se houver tempo

def handle_usuario_criado(data):
    email = data.get('email')
    nome = data.get('nome')
    perfil = data.get('perfil')

    if not email:
        return
    
    sucesso = EmailService.enviar(
        destinatario = email,
        assunto = "Bem vindo ao Sistema ERP - Credenciais de Acesso",
        corpo = f"Ola {nome},\n\n"
        f"A sua conta foi criada com sucesso.\n"
        f"Email de acesso: {email}\n"
        f"Perfil: {perfil}\n\n"
        f"Por favor altere a sua password no primeiro acesso.\n"
        f"Atenciosamente, a Associação Agricola"
    )

    Notificacao.objects.create(
        destinatarioId = data.get('usuarioId'),
        tipoDestinatario = 'USUARIO',
        canal = 'EMAIL',
        titulo = "Credenciais de acesso enviadas",
        mensagem = f"Email de boas-vindas enviado para {email}",
        evento = 'usuario.criado',
        payload = data,
        enviado = sucesso,
        erro = None if sucesso else 'Falha no envio de email'
    )

def handle_login_failed(data):

    Notificacao.objects.create(
        destinatarioId = None,
        tipoDestinatario = 'SISTEMA',
        canal = 'INTERNO',
        titulo = 'Tentativa de acesso falha',
        mensagem = f"Tentativa falha de login para o email {data.get('email')} em {data.get('timestamp')}",
        evento = 'auth.login.failed',
        payload = data,
        enviado = True
    )


HANDLERS = {
    'auth.login.failed': handle_login_failed,
    'usuario.criado': handle_usuario_criado,
    'os.aprovada': handle_os_aprovada,
    'os.concluida': handle_os_concluida,
    'os.cancelada': handle_os_cancelada,
    'financeiro.conta.paga': handle_conta_paga,
    'financeiro.mensalidades.geradas': handle_mensalidades_geradas
}

def processar_evento(ch, method, properties, body):

    try:
        data = json.loads(body)
        routing_key = method.routing_key
        handler = HANDLERS.get(routing_key)

        if handler:
            handler(data=data)
    
    except Exception as e:
        print(f"Erro ao processar evento {method.routing_key}: {str(e)}")


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
        queue_name = 'notification_service_queue',
        routing_keys = list(HANDLERS.keys()),
        callback = processar_evento
    )
