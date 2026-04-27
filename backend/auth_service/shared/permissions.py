from rest_framework.permissions import BasePermission


class HasPerfil(BasePermission):
    perfis_requeridos = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        perfil = request.auth.get('perfil') if request.auth else None
        return perfil in self.perfis_requeridos


class IsOperador(HasPerfil):
    perfis_requeridos = ['OPERADOR', 'GESTOR', 'ADMINISTRADOR']


class IsGestor(HasPerfil):
    perfis_requeridos = ['GESTOR', 'ADMINISTRADOR']


class IsFinanceiro(HasPerfil):
    perfis_requeridos = ['FINANCEIRO', 'ADMINISTRADOR']


class IsDirecao(HasPerfil):
    perfis_requeridos = ['DIRECAO', 'ADMINISTRADOR']


class IsAdministrador(HasPerfil):
    perfis_requeridos = ['ADMINISTRADOR']
