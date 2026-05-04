from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    usuarioId = serializers.UUIDField()
    delegacaoId = serializers.UUIDField()
    perfil = serializers.CharField()


class RefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


class MeSerializer(serializers.Serializer):
    usuarioId = serializers.UUIDField()
    email = serializers.EmailField()
    perfil = serializers.CharField()
    delegacaoId = serializers.UUIDField()
    ativo = serializers.BooleanField()
