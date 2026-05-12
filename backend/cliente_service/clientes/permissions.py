import jwt
from django.conf import settings
from rest_framework.permissions import BasePermission


class IsAuthenticatedWithJWT(BasePermission):
    """Copiado de shared/auth_middleware.
    Valida o token JWT emitido pelo autn-service."""
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
        token = auth_header.split(' ')[1]
        try:
            jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
            return True
        except jwt.ExpiredTokenError:
            return False
        except jwt.InvalidTokenError:
            return False