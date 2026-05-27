from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    responses={200: {'type': 'object', 'properties': {'status': {'type': 'string'}, 'service': {'type': 'string'}}}},
    tags=['health'],
    auth=[],
    description='Verifica se o serviço está operacional. Não requer autenticação.',
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'service': 'os-service'})


urlpatterns = [
    path('api/ordens/health/', health_check, name='health-check'),
    path('api/', include('ordens.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
