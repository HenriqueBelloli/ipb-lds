import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

logger = logging.getLogger(__name__)


class _JWTUser:
    """
    Objecto simples que representa um utilizador autenticado via JWT.
    Não acede à base de dados — usa apenas os claims do token.
    Compatível com request.user.is_authenticated.
    """

    def __init__(self, payload: dict):
        self.payload = payload
        self.is_authenticated = True
        self.is_anonymous = False
        self.pk = payload.get('usuarioId')

    def __str__(self):
        return self.payload.get('email', str(self.pk))


class JWTMiddleware:
    """
    Middleware reutilizável entre microserviços.
    Valida o JWT no header Authorization sem aceder à base de dados.
    Injeta request.user (_JWTUser) e request.auth (payload dict).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._jwt_auth = JWTAuthentication()

    def __call__(self, request):
        try:
            raw_token = self._jwt_auth.get_raw_token(self._jwt_auth.get_header(request))
            if raw_token is not None:
                validated_token = self._jwt_auth.get_validated_token(raw_token)
                payload = validated_token.payload
                request.user = _JWTUser(payload)
                request.auth = payload
        except (InvalidToken, AuthenticationFailed) as exc:
            logger.debug('JWT inválido ou ausente: %s', exc)

        return self.get_response(request)
