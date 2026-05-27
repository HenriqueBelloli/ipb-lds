import json
import logging

from shared.rabbitmq import start_consumer

from .models import Credencial

logger = logging.getLogger(__name__)


def handle_usuario_criado(ch, method, properties, body):
    try:
        data = json.loads(body)
        usuario_id = data.get('usuarioId')
        email = data.get('email')
        delegacao_id = data.get('delegacaoId')
        perfil = data.get('perfil', 'OPERADOR')

        if not usuario_id or not email:
            logger.warning(f'Evento usuario.criado incompleto: {data}')
            return

        if Credencial.objects.filter(usuarioId=usuario_id).exists():
            logger.info(f'Credencial já existe para usuarioId {usuario_id}')
            return

        # Usa set_password() do AbstractBaseUser em vez de make_password() + passwordHash
        password_temp = 'temp_' + usuario_id[:8]
        credencial = Credencial(
            usuarioId=usuario_id,
            delegacaoId=delegacao_id,
            email=email,
            perfil=perfil,
        )
        credencial.set_password(password_temp)
        credencial.save()
        logger.info(f'Credencial criada para {email}')
    except Exception as e:
        logger.error(f'Erro ao processar usuario.criado: {str(e)}')


def start_auth_consumer():
    start_consumer(
        queue_name='auth_usuario_events',
        routing_keys=['usuario.criado'],
        callback=handle_usuario_criado
    )
