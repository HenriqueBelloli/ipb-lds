# servico_service/urls.py
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

@extend_schema(exclude=True)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'service': 'servico-service'})

urlpatterns = [
    path('api/servicos/health/', health_check, name='health-check'),
    path('api/servicos/', include('servicos.urls')),
    path('api/servicos/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/servicos/schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
]
