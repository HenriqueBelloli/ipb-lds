from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/', include('auditoria.urls')),
    path('api/auditoria/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/auditoria/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
