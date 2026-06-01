from datetime import datetime, timezone
from shared.rabbitmq import publish_event


def publish_login_success(usuario_id: str, email: str, perfil: str) -> None:
    publish_event('auth.login.success', {
        'usuarioId': usuario_id,
        'email': email,
        'perfil': perfil,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    })


def publish_login_failed(email: str, motivo: str = 'Credenciais inválidas') -> None:
    publish_event('auth.login.failed', {
        'email': email,
        'motivo': motivo,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    })
