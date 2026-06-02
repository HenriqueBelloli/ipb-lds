from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_spectacular.utils import extend_schema

from .models import Credencial
from .publisher import publish_login_failed, publish_login_success
from .serializers import ChangePasswordSerializer, LoginSerializer, MeSerializer, RefreshRequestSerializer, RefreshResponseSerializer, TokenResponseSerializer


def _gerar_tokens(credencial: Credencial) -> dict:
    refresh = RefreshToken()
    refresh['usuarioId'] = str(credencial.usuarioId)
    refresh['email'] = credencial.email
    refresh['delegacaoId'] = str(credencial.delegacaoId)
    refresh['perfil'] = credencial.perfil
    refresh['ativo'] = credencial.ativo

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'usuarioId': str(credencial.usuarioId),
        'delegacaoId': str(credencial.delegacaoId),
        'perfil': credencial.perfil,
    }


def _extrair_claims_refresh(refresh_token) -> dict:
    """Extrai todos os claims customizados de um refresh token para retornar na resposta."""
    return {
        'usuarioId': refresh_token.get('usuarioId'),
        'delegacaoId': refresh_token.get('delegacaoId'),
        'perfil': refresh_token.get('perfil'),
    }


@extend_schema(request=LoginSerializer, responses={200: TokenResponseSerializer})
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        email = request.data.get('email', '')
        publish_login_failed(email, 'Dados de entrada inválidos')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    try:
        credencial = Credencial.objects.get(email=email)
    except Credencial.DoesNotExist:
        publish_login_failed(email, 'Utilizador não encontrado')
        return Response({'detail': 'Credenciais inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not credencial.ativo:
        publish_login_failed(email, 'Utilizador inativo')
        return Response({'detail': 'Utilizador inativo.'}, status=status.HTTP_403_FORBIDDEN)

    if not credencial.check_password(password):
        publish_login_failed(email, 'Password incorreta')
        return Response({'detail': 'Credenciais inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = _gerar_tokens(credencial)
    publish_login_success(str(credencial.usuarioId), credencial.email, credencial.perfil)
    return Response(tokens, status=status.HTTP_200_OK)


@extend_schema(request=RefreshRequestSerializer, responses={200: TokenResponseSerializer})
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh(request):
    try:
        refresh_token = RefreshToken(request.data.get('refresh'))
        
        # O simplejwt.access_token copia claims automaticamente do refresh token,
        # mas para garantir que todos os claims customizados estão presentes,
        # verificamos e retornamos os dados que serão usados pelos outros serviços.
        access_token = refresh_token.access_token
        
        # Verificar se os claims necessários estão no access token
        # Se não estiverem, adicionar explicitamente
        if 'usuarioId' not in access_token:
            access_token['usuarioId'] = refresh_token.get('usuarioId')
        if 'delegacaoId' not in access_token:
            access_token['delegacaoId'] = refresh_token.get('delegacaoId')
        if 'perfil' not in access_token:
            access_token['perfil'] = refresh_token.get('perfil')
        if 'email' not in access_token:
            access_token['email'] = refresh_token.get('email')
        if 'ativo' not in access_token:
            access_token['ativo'] = refresh_token.get('ativo')
        
        claims = _extrair_claims_refresh(refresh_token)
        return Response({
            'access': str(access_token),
            'refresh': str(refresh_token),
            **claims,
        }, status=status.HTTP_200_OK)
    except TokenError:
        return Response(
            {'detail': 'Token inválido ou expirado.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(responses={200: MeSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    token = request.auth
    return Response({
        'usuarioId': token.get('usuarioId'),
        'email': token.get('email'),
        'perfil': token.get('perfil'),
        'delegacaoId': token.get('delegacaoId'),
        'ativo': token.get('ativo'),
    }, status=status.HTTP_200_OK)


@extend_schema(request=ChangePasswordSerializer, responses={204: None})
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    usuario_id = request.auth.get('usuarioId')
    credencial = Credencial.objects.filter(usuarioId=usuario_id, ativo=True).first()

    if credencial is None:
        return Response({'detail': 'Credenciais nao encontradas.'}, status=status.HTTP_404_NOT_FOUND)

    current_password = serializer.validated_data['currentPassword']
    if not credencial.check_password(current_password):
        return Response({'currentPassword': ['Password atual incorreta.']}, status=status.HTTP_400_BAD_REQUEST)

    credencial.set_password(serializer.validated_data['newPassword'])
    credencial.save(update_fields=['password'])
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=RefreshRequestSerializer,
    responses={204: None},
    description='Invalida o refresh token. Requer autenticação Bearer.',
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except TokenError:
        return Response(status=status.HTTP_204_NO_CONTENT)
