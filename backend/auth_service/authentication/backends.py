from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from .models import Credencial


class CredencialJWTAuthentication(JWTAuthentication):
    """
    Backend de autenticação JWT customizado que resolve o utilizador
    na tabela Credencial pelo claim 'usuarioId' em vez de usar o
    modelo auth.User do Django (que tem id inteiro e é incompatível).
    """

    def get_user(self, validated_token):
        try:
            usuario_id = validated_token['usuarioId']
        except KeyError:
            raise InvalidToken('O token não contém o claim usuarioId.')

        try:
            credencial = Credencial.objects.get(usuarioId=usuario_id)
        except Credencial.DoesNotExist:
            raise InvalidToken('Credencial não encontrada para o utilizador do token.')

        if not credencial.ativo:
            raise InvalidToken('Utilizador inativo.')

        return credencial
