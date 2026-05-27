from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import LogAuditoria
from .serializers import LogAuditoriaSerializer
from shared.auth_middleware.permissions import IsAdministrador


@extend_schema(
    responses={200: {'type': 'object', 'properties': {'status': {'type': 'string'}, 'service': {'type': 'string'}}}},
    tags=['health'],
    auth=[],
    description='Verifica se o serviço está operacional. Não requer autenticação.',
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({'status': 'ok', 'service': 'auditoria-service'})


class LogAuditoriaListView(generics.ListAPIView):
    serializer_class = LogAuditoriaSerializer
    permission_classes = [IsAuthenticated, IsAdministrador]

    def get_queryset(self):
        queryset = LogAuditoria.objects.all()
        evento = self.request.query_params.get('evento')
        servico = self.request.query_params.get('servico')
        usuario_id = self.request.query_params.get('usuarioId')
        delegacao_id = self.request.query_params.get('delegacaoId')
        data_inicio = self.request.query_params.get('dataInicio')
        data_fim = self.request.query_params.get('dataFim')

        if evento:
            queryset = queryset.filter(evento=evento)
        if servico:
            queryset = queryset.filter(servico=servico)
        if usuario_id:
            queryset = queryset.filter(usuarioId=usuario_id)
        if delegacao_id:
            queryset = queryset.filter(delegacaoId=delegacao_id)
        if data_inicio:
            queryset = queryset.filter(timestamp__date__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(timestamp__date__lte=data_fim)

        return queryset


class LogAuditoriaDetailView(generics.RetrieveAPIView):
    serializer_class = LogAuditoriaSerializer
    permission_classes = [IsAuthenticated, IsAdministrador]
    queryset = LogAuditoria.objects.all()
    lookup_field = 'id'
