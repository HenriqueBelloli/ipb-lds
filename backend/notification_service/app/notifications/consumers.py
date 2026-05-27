from .models import Notificacao
from .services.cliente_client import ClienteServiceClient
from .services.email_service import EmailService
import json
import logging

logger = logging.getLogger(__name__)


def handle_os_aprovada(data):
    status_resultante = data.get('statusResultante')

    if status_resultante != 'PAGAMENTO_PENDENTE':
        return

    Notificacao.objects.create(
        destinatarioId=None,
        tipoDestinatario='SISTEMA',
        canal='INTERNO',
        titulo='OS aguarda pagamento de entrada',
        mensagem=f"OS {data.get('osId')} aprovada e a aguardar pagamento de entrada no valor de {data.get('valorTotal')}",
        evento='os.aprovada',
        payload=data,
        enviado=True
    )


def handle_os_cancelada(data):
    os_id = data.get('osId')
    cliente_id = data.get('clienteId')
    motivo = data.get('motivo', 'nao especificado')

    Notificacao.objects.create(
        destinatarioId=None,
        tipoDestinatario='SISTEMA',
        canal='INTERNO',
        titulo='Ordem de Serviço Cancelada',
        mensagem=f"A OS {os_id} foi cancelada. Motivo: {motivo}",
        evento='os.cancelada',
        payload=data,
        enviado=True
    )

    cliente = ClienteServiceClient.get_cliente_anonimo(cliente_id)
    if cliente and cliente.get('email'):
        sucesso = EmailService.enviar(
            destinatario=cliente['email'],
            assunto="A sua Ordem de Serviço foi cancelada",
            corpo=f"Informamos que a sua OS foi cancelada.\nMotivo: {motivo}\n\nPara mais informacoes contate a sua delegacao."
        )

        Notificacao.objects.create(
            destinatarioId=cliente_id,
            tipoDestinatario='CLIENTE',
            canal='EMAIL',
            titulo='OS Cancelada',
            mensagem=f"Email enviado ao cliente sobre cancelamento da OS {os_id}",
            evento='os.cancelada',
            payload=data,
            enviado=sucesso,
            erro=None if sucesso else 'Falha no envio de email'
        )


def handle_os_concluida(data):
    Notificacao.objects.create(
        destinatarioId=None,
        tipoDestinatario='SISTEMA',
        canal='INTERNO',
        titulo='OS concluida - aguarda faturacao',
        mensagem=f"A OS {data.get('osId')} foi concluida e esta a aguardar faturacao pelo modulo financeiro",
        evento='os.concluida',
        payload=data,
        enviado=True
    )


def handle_mensalidades_geradas(data):
    mes = data.get('mesReferencia')
    total = data.get('totalGeradas', 0)
    ignoradas = data.get('totalIgnoradas', 0)

    Notificacao.objects.create(
        destinatarioId=None,
        tipoDestinatario='SISTEMA',
        canal='INTERNO',
        titulo="Mensalidades geradas automaticamente",
        mensagem=f"Geradas {total} mensalidades para {mes}. {ignoradas} ignoradas por ja existirem.",
        evento='financeiro.mensalidades.geradas',
        payload=data,
        enviado=True
    )


def handle_usuario_criado(data):
    email: str = data.get('email')
    nome: str = data.get('nome')
    perfil: str = data.get('perfil')

    if not email:
        return

    sucesso = EmailService.enviar(
        destinatario=email,
        assunto="Bem vindo ao Sistema ERP - Credenciais de Acesso",
        corpo=(
            f"Ola {nome},\n\n"
            f"A sua conta foi criada com sucesso.\n"
            f"Email de acesso: {email}\n"
            f"Perfil: {perfil}\n\n"
            f"Por favor altere a sua password no primeiro acesso.\n\n"
            f"Associação Agrícola"
        )
    )

    Notificacao.objects.create(
        destinatarioId=data.get('usuarioId'),
        tipoDestinatario='USUARIO',
        canal='EMAIL',
        titulo="Credenciais de acesso enviadas",
        mensagem=f"Email de boas-vindas enviado para {email}",
        evento='usuario.criado',
        payload=data,
        enviado=sucesso,
        erro=None if sucesso else 'Falha no envio de email'
    )


HANDLERS = {
    'usuario.criado': handle_usuario_criado,
    'os.aprovada': handle_os_aprovada,
    'os.concluida': handle_os_concluida,
    'os.cancelada': handle_os_cancelada,
    'financeiro.mensalidades.geradas': handle_mensalidades_geradas,
}


def processar_evento(ch, method, properties, body):
    try:
        data = json.loads(body)
        routing_key = method.routing_key
        handler = HANDLERS.get(routing_key)
        if handler:
            handler(data=data)
    except Exception as e:
        logger.error(f"Erro ao processar evento {method.routing_key}: {str(e)}")


def iniciar_consumers():
    from shared.rabbitmq import start_consumer
    start_consumer(
        'notification_service_queue',
        list(HANDLERS.keys()),
        processar_evento
    )
