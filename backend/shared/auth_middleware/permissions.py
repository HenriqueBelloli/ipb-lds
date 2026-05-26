from rest_framework.permissions import BasePermission


class HasPerfil(BasePermission):
    """Classe base para verificação de perfil via claims do JWT."""

    perfis_requeridos: list = []

    def has_permission(self, request, view):
        auth = getattr(request, 'auth', None)
        if not auth:
            return False
        return auth.get('perfil') in self.perfis_requeridos


class IsOperador(HasPerfil):
    """Acesso para OPERADOR, GESTOR e ADMINISTRADOR."""

    perfis_requeridos = ['OPERADOR', 'GESTOR', 'ADMINISTRADOR']


class IsGestor(HasPerfil):
    """Acesso para GESTOR e ADMINISTRADOR."""

    perfis_requeridos = ['GESTOR', 'ADMINISTRADOR']


class IsFinanceiro(HasPerfil):
    """Acesso para FINANCEIRO e ADMINISTRADOR."""

    perfis_requeridos = ['FINANCEIRO', 'ADMINISTRADOR']


class IsDirecao(HasPerfil):
    """Acesso para DIRECAO e ADMINISTRADOR."""

    perfis_requeridos = ['DIRECAO', 'ADMINISTRADOR']


class IsAdministrador(HasPerfil):
    """Acesso exclusivo para ADMINISTRADOR."""

    perfis_requeridos = ['ADMINISTRADOR']


class IsMesmaDelegacao(BasePermission):
    """
    Verifica se o utilizador pertence à mesma delegação do recurso.
    O objeto acedido deve expor um atributo `delegacaoId` (UUID ou str).

    Uso típico em views de detalhe:
        permission_classes = [IsAuthenticated, IsMesmaDelegacao]
    """

    def has_permission(self, request, view):
        return bool(getattr(request, 'auth', None))

    def has_object_permission(self, request, view, obj):
        auth = getattr(request, 'auth', None)
        if not auth:
            return False

        token_delegacao = str(auth.get('delegacaoId', ''))
        obj_delegacao = str(getattr(obj, 'delegacaoId', '') or '')
        return token_delegacao == obj_delegacao
