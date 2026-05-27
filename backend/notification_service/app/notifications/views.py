from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from .models import Notificacao
from .serializers import (
    NotificationListSerializer,
    NotificationDetailErrorSerializer,
    NotificacaoMarkAsReadSerializer,
    NotificacaoMarkAsReadErrorSerializer,
    NotificationMarkAllAsReadSerializer,
)
from shared.auth_middleware.permissions import IsOperador


@extend_schema(
    responses={200: {'type': 'object', 'properties': {'status': {'type': 'string'}, 'service': {'type': 'string'}}}},
    tags=['health'],
    auth=[],
    description='Verifica se o serviço está operacional. Não requer autenticação.',
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({'status': 'ok', 'service': 'notification-service'})


class NotificationListView(APIView):
    def get_permissions(self):
        return [IsOperador()]

    @extend_schema(
            operation_id="listar_notificacoes",
            request=None,
            responses={200: NotificationListSerializer}
    )
    def get(self, request):
        usuario_id = request.auth.get('usuarioId')
        qs = Notificacao.objects.filter(
            Q(tipoDestinatario='SISTEMA') | Q(destinatarioId=usuario_id)
        ).order_by('-createdAt')

        lida = request.query_params.get('lida')
        canal = request.query_params.get('canal')
        tipoDestinatario = request.query_params.get('tipoDestinatario')
        destinatarioId = request.query_params.get('destinatarioId')
        evento = request.query_params.get('evento')

        if lida is not None:
            qs = qs.filter(lida=lida.lower() in ('true', '1'))
        if canal:
            qs = qs.filter(canal=canal)
        if tipoDestinatario:
            qs = qs.filter(tipoDestinatario=tipoDestinatario)
        if destinatarioId:
            qs = qs.filter(destinatarioId=destinatarioId)
        if evento:
            qs = qs.filter(evento=evento)

        serializer = NotificationListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationDetailView(APIView):
    def get_permissions(self):
        return [IsOperador()]

    def _get_object(self, id, usuario_id):
        return get_object_or_404(
            Notificacao,
            Q(tipoDestinatario='SISTEMA') | Q(destinatarioId=usuario_id),
            id=id
        )

    @extend_schema(
            operation_id="detalhar_notificacao",
            request=None,
            responses={200: NotificationListSerializer, 404: NotificationDetailErrorSerializer}
    )
    def get(self, request, id):
        usuario_id = request.auth.get('usuarioId')
        notificacao = self._get_object(id=id, usuario_id=usuario_id)
        serializer = NotificationListSerializer(notificacao, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationMarkAsReadView(APIView):
    def get_permissions(self):
        return [IsOperador()]

    def _get_object(self, id, usuario_id):
        return get_object_or_404(
            Notificacao,
            Q(tipoDestinatario='SISTEMA') | Q(destinatarioId=usuario_id),
            id=id
        )

    @extend_schema(
            operation_id="marcar_como_lida",
            request=None,
            responses={200: NotificacaoMarkAsReadSerializer, 409: NotificacaoMarkAsReadErrorSerializer}
    )
    def patch(self, request, id):
        usuario_id = request.auth.get('usuarioId')
        notificacao = self._get_object(id=id, usuario_id=usuario_id)

        if notificacao.lida:
            return Response(
                data={"message": "A notificação já se encontra marcada como lida."},
                status=status.HTTP_409_CONFLICT
            )

        notificacao.lida = True
        notificacao.save(update_fields=["lida"])
        serializer = NotificacaoMarkAsReadSerializer(notificacao, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationMarkAllAsReadView(APIView):
    def get_permissions(self):
        return [IsOperador()]

    @extend_schema(
            operation_id="marcar_todas_como_lida",
            request=None,
            responses={200: NotificationMarkAllAsReadSerializer}
    )
    def patch(self, request):
        usuario_id = request.auth.get('usuarioId')
        qs = Notificacao.objects.filter(
            Q(tipoDestinatario='SISTEMA') | Q(destinatarioId=usuario_id),
            lida=False
        )
        qs.update(lida=True)

        qs_updated = Notificacao.objects.filter(
            Q(tipoDestinatario='SISTEMA') | Q(destinatarioId=usuario_id)
        )
        serializer = NotificationMarkAllAsReadSerializer(qs_updated, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
