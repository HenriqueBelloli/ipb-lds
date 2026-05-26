from functools import wraps

from rest_framework import status
from rest_framework.response import Response


def require_perfil(perfis_permitidos: list):
    """
    Decorador que restringe o acesso a uma view a utilizadores
    cujo perfil esteja na lista `perfis_permitidos`.

    Exemplo de uso:
        @require_perfil(['GESTOR', 'FINANCEIRO'])
        def minha_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not getattr(request, 'auth', None):
                return Response(
                    {'detail': 'Autenticação necessária.'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            perfil_usuario = request.auth.get('perfil')
            if perfil_usuario not in perfis_permitidos:
                return Response(
                    {'detail': 'Permissões insuficientes.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
