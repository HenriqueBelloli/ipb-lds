from .models import Usuario, Delegacao
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

class DelegacaoListSerializer(serializers.ModelSerializer):
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

class UsuarioListSerializer(serializers.ModelSerializer):
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

class UsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'perfil', 'delegacaoId', 'ativo']

    def validate_email(self, value):
        qs = Usuario.objects.filter(email = value).exclude(pk = self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Este email já está em uso")
        
        return value


class UsuarioProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['nome']


class DelegacaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delegacao
        fields = [
            'id', 'codigo', 'nome', 'localizacao',
            'responsavelId', 'ativo', 'createdAt'
        ]

        read_only_fields = [
            'id',
            'createdAt'
        ]

class DelegacaoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delegacao
        fields = [
            'codigo',
            'nome',
            'localizacao',
            'responsavelId',
            'ativo'
        ]
    
    def validate_codigo(self, value):
        qs = Delegacao.objects.filter(codigo = value).exclude(pk = self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Este código já está em uso.")
        
        return value
