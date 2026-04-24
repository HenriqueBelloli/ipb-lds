from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from .models import Credencial


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            credencial = Credencial.objects.get(email=data['email'])
        except Credencial.DoesNotExist:
            raise serializers.ValidationError('Credenciais inválidas.')

        if not credencial.ativo:
            raise serializers.ValidationError('Utilizador inativo.')

        if not check_password(data['password'], credencial.passwordHash):
            raise serializers.ValidationError('Credenciais inválidas.')

        data['credencial'] = credencial
        return data


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    usuarioId = serializers.UUIDField()
    delegacaoId = serializers.UUIDField()
    perfil = serializers.CharField()


class RefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
