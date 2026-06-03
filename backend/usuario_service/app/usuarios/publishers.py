from shared.rabbitmq import publish_event
from .models import Usuario


def publish_usuario_criado(usuario: Usuario):
    publish_event('usuario.criado', {
        'servico': 'usuario-service',
        'usuarioId': str(usuario.id),
        'nome': usuario.nome,
        'perfil': usuario.perfil,
    })


def publish_usuario_desativado(usuario: Usuario):
    publish_event('usuario.desativado', {
        'servico': 'usuario-service',
        'usuarioId': str(usuario.id),
        'nome': usuario.nome,
        'email': usuario.email,
    })