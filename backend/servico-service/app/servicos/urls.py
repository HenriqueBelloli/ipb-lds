# servicos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ServicoListCreateView.as_view(), name='servico-list-create'),
    path('<uuid:pk>/', views.ServicoDetailView.as_view(), name='servico-detail'),
    path('delegacao/', views.ServicoDelegacaoListCreateView.as_view(),
         name='servico-delegacao-create'),
    path('delegacao/<uuid:delegacaoId>/',
         views.ServicoDelegacaoListCreateView.as_view(),
         name='servico-delegacao-list'),
    path('delegacao/<uuid:delegacaoId>/<uuid:pk>/',
         views.ServicoDelegacaoDetailView.as_view(),
         name='servico-delegacao-detail'),
]
