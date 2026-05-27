from django.urls import path
from .views import(
    ClienteListCreateView,
    ClienteDetailView,
    ClienteDelegacaoView,

)

urlpatterns = [
    path('clientes/', ClienteListCreateView.as_view()),
    path('clientes/<uuid:pk>/', ClienteDetailView.as_view()),
    path('clientes/<uuid:pk>/delegacoes/', ClienteDelegacaoView.as_view()),
]