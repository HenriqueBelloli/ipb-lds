from django.urls import path
from rest_framework import routers

from .views import (
    UsuarioListCreateView,
    UsuarioDetailUpdateView,
    DelegacaoListCreateView,
    DelegacaoUpdateView,
    health,
)

urlpatterns = [
    # Utilizadores
    path('usuarios/health/', health, name='usuario-health'),
    path('usuarios/', UsuarioListCreateView.as_view(), name='usuario-list-create'),
    path('usuarios/<uuid:pk>/', UsuarioDetailUpdateView.as_view(), name='usuario-detail-update'),

    # Delegações
    path('delegacoes/', DelegacaoListCreateView.as_view(), name='delegacao-list-create'),
    path('delegacoes/<uuid:pk>/', DelegacaoUpdateView.as_view(), name='delegacao-update'),
]