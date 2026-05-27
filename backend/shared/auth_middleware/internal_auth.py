import os
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class _InternalServiceUser:
    is_authenticated = True


class InternalServiceAuthentication(BaseAuthentication):
    """Autentica chamadas sistema-a-sistema via header X-Internal-Secret.

    Uso: adicionar a authentication_classes numa view que precisa aceitar
    chamadas de outros serviços sem JWT (ex: schedulers, jobs automáticos).
    Requer INTERNAL_SERVICE_SECRET no ambiente.
    """

    def authenticate(self, request):
        secret = request.META.get('HTTP_X_INTERNAL_SECRET', '')
        if not secret:
            return None  # não é uma chamada interna — deixa o JWT auth tratar

        expected = os.environ.get('INTERNAL_SERVICE_SECRET', '')
        if not expected or secret != expected:
            raise AuthenticationFailed('Internal secret inválido.')

        return (_InternalServiceUser(), {'perfil': 'FINANCEIRO', 'usuarioId': 'internal-service'})
