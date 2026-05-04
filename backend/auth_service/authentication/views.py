from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_spectacular.utils import extend_schema

from .models import Credencial
from .publisher import publish_login_failed, publish_login_success
from .serializers import LoginSerializer, MeSerializer, RefreshResponseSerializer, TokenResponseSerializer


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

    if not check_password(password, credencial.passwordHash):
        publish_login_failed(email, 'Password incorreta')
        return Response({'detail': 'Credenciais inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = _gerar_tokens(credencial)
    publish_login_success(str(credencial.usuarioId), credencial.email, credencial.perfil)
    return Response(tokens, status=status.HTTP_200_OK)


@extend_schema(
    request={'type': 'object', 'properties': {'refresh': {'type': 'string'}}},
    responses={200: RefreshResponseSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh(request):
    try:
        refresh_token = RefreshToken(request.data.get('refresh'))
        access_token = str(refresh_token.access_token)
        return Response({'access': access_token}, status=status.HTTP_200_OK)
    except TokenError:
        return Response(
            {'detail': 'Token inválido ou expirado.'},
            status=status.HTTP_401_UNAUTHORIZED
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
