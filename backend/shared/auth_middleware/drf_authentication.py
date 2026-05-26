import logging

from rest_framework_simplejwt.authentication import JWTAuthentication

from .middleware import _JWTUser

logger = logging.getLogger(__name__)


class JWTStatelessAuthentication(JWTAuthentication):
    """
    DRF authentication class: valida JWT sem acesso à base de dados.
    Para microserviços que consomem tokens emitidos pelo auth-service.
    Define request.user (_JWTUser) e request.auth (payload dict) no sistema DRF.

    Uso em settings.py de cada serviço (excepto auth-service):
        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'shared.auth_middleware.drf_authentication.JWTStatelessAuthentication',
            ],
        }
    """

    def get_user(self, validated_token):
        return _JWTUser(validated_token.payload)
