import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission


class JWTUser:
    def __init__(self, payload):
        self.id = payload.get('sub')
        self.email = payload.get('email', '')
        self.roles = payload.get('roles', [])
        self.is_authenticated = True

    @property
    def pk(self):
        return self.id


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ', 1)[1].strip()
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expirado.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token inválido.')
        return JWTUser(payload), token

    def authenticate_header(self, request):
        return 'Bearer'


class IsOperador(BasePermission):
    message = 'Acesso negado. É necessário o perfil OPERADOR.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return any(r in getattr(user, 'roles', []) for r in ('OPERADOR', 'ADMIN'))