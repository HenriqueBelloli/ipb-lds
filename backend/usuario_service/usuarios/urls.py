from django.urls import path
from .views import (
    UsuarioListCreateView,
    UsuarioDetailUpdateView,
    DelegacaoListCreateView,
    DelegacaoUpdateView,
)

urlpatterns = [
    # Utilizadores
    path('usuarios/', UsuarioListCreateView.as_view(), name='usuario-list-create'),
    path('usuarios/<uuid:pk>/', UsuarioDetailUpdateView.as_view(), name='usuario-detail-update'),

    # Delegações
    path('delegacoes/', DelegacaoListCreateView.as_view(), name='delegacao-list-create'),
    path('delegacoes/<uuid:pk>/', DelegacaoUpdateView.as_view(), name='delegacao-update'),
]