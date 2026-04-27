from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def require_perfil(perfis_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'auth') or not request.auth:
                return Response(
                    {'detail': 'Autenticação necessária.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            perfil_usuario = request.auth.get('perfil')
            if perfil_usuario not in perfis_permitidos:
                return Response(
                    {'detail': 'Permissões insuficientes.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
