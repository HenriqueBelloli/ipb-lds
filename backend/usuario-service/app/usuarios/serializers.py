from .models import Usuario, Delegacao
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

class DelegacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delegacao
        fields = [
            'id',
            'codigo',
            'nome',
            'localizacao',
            'responsavelId',
            'ativo',
            'createdAt'
        ]
        read_only_fields = ['id', 'createdAt']

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id',
            'nome',
            'email',
            'perfil',
            'delegacaoId',
            'ativo',
            'createdAt'
        ]
        read_only_fields= ['id', 'createdAt']

class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = Usuario
        fields = [
            'nome',
            'email',
            'password',
            'perfil',
            'delegacaoId'
        ]
    
    def create(self, validated_data):

        validated_data['passwordHash'] = make_password(
            validated_data.pop('password')
        )

        return super().create(validated_data)

