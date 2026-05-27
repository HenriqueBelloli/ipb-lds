from shared.rabbitmq import publish_event
from .models import Cliente


def publish_cliente_criado(cliente: Cliente, usuario_id: str, delegacao_id: str):
    publish_event('cliente.criado', {
        'servico': 'cliente-service',
        'clienteId': str(cliente.id),
        'nome': cliente.nome,
        'nif': cliente.nif,
        'flagAssociado': cliente.flagAssociado,
        'usuarioId': usuario_id,
        'delegacaoId': delegacao_id,
    })
