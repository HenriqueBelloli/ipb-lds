from django.urls import path
from .views import (ServicoListCreateView, ServicoDetailView, ServicoDelegacaoListCreateView, ServicoDelegacaoDetailView,)

urlpatterns = [
    path('', ServicoListCreateView.as_view(), name='servico-list-create'),
    path('<uuid:pk>/', ServicoDetailView.as_view(), name='servico-detail'),
    path('delegacao/', ServicoDelegacaoListCreateView.as_view(), name='servico-delegacao-create'),
    path('delegacao/<uuid:delegacaoId/', ServicoDelegacaoListCreateView.as_view(), name='servico-delegacao-list'),
    path('delegacao/uuid:delegacaoId>/<uuis:pk>/', ServicoDelegacaoDetailView.as_view(), name='servico-delegacao-detail'),
    path('delegacao/editar/<uuid:pk>/', ServicoDelegacaoDetailView.as_view(), name='servico-delegacao-update',)
]
