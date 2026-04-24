from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_spectacular.utils import extend_schema

from .serializers import LoginSerializer, TokenResponseSerializer, RefreshResponseSerializer
from .models import Credencial


def _gerar_tokens(credencial: Credencial) -> dict:
    refresh = RefreshToken()
    refresh['usuarioId'] = str(credencial.usuarioId)
    refresh['delegacaoId'] = str(credencial.delegacaoId)
    refresh['perfil'] = credencial.perfil

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
    serializer.is_valid(raise_exception=True)

    credencial = serializer.validated_data['credencial']
    tokens = _gerar_tokens(credencial)

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
