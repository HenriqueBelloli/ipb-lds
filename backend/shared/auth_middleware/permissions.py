from rest_framework.permissions import BasePermission

PERFIL_ORDER = {
    'OPERADOR': 1,
    'GESTOR': 2,
    'FINANCEIRO': 3,
    'DIRECAO': 4,
    'ADMINISTRADOR': 5,
}


class HasPerfilMinimo(BasePermission):
    """Permite acesso se o perfil do token >= perfil_minimo na hierarquia."""

    perfil_minimo: str = 'ADMINISTRADOR'

    def has_permission(self, request, view):
        auth = getattr(request, 'auth', None)
        if not auth:
            return False
        nivel_user = PERFIL_ORDER.get(auth.get('perfil'), 0)
        nivel_req = PERFIL_ORDER.get(self.perfil_minimo, 99)
        return nivel_user >= nivel_req


class IsOperador(HasPerfilMinimo):
    perfil_minimo = 'OPERADOR'


class IsGestor(HasPerfilMinimo):
    perfil_minimo = 'GESTOR'


class IsFinanceiro(HasPerfilMinimo):
    perfil_minimo = 'FINANCEIRO'


class IsDirecao(HasPerfilMinimo):
    perfil_minimo = 'DIRECAO'


class IsAdministrador(HasPerfilMinimo):
    perfil_minimo = 'ADMINISTRADOR'


class IsMesmaDelegacao(BasePermission):
    """
    Verifica se o utilizador pertence à mesma delegação do recurso.
    O objeto acedido deve expor um atributo `delegacaoId` (UUID ou str).

    Uso típico em views de detalhe:
        permission_classes = [IsOperador, IsMesmaDelegacao]
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
