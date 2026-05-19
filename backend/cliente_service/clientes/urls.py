from django.urls import path
from .views import ClienteViewSet

cliente_list = ClienteViewSet.as_view({'get':'list', 'post': 'create',})
cliente_detail = ClienteViewSet.as_view({'get': 'retrieve', 'put':'update'})
cliente_delegs = ClienteViewSet.as_view({'get': 'delegacoes', 'post': 'delegacoes'})


urlpatterns = [
    path('clientes/', cliente_list),
    path('clientes/<uuid:pk>/', cliente_detail),
    path('clientes/<uuid:pk>/delegacoes/', cliente_delegs),
]