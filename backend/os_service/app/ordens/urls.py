from django.urls import path
from . import views

urlpatterns = [
    path('ordens/', views.OrdemServicoListCreateView.as_view()),
    path('ordens/<uuid:pk>/', views.OrdemServicoDetailView.as_view()),
    path('ordens/<uuid:pk>/status/', views.OrdemServicoStatusView.as_view()),
    path('ordens/<uuid:pk>/cancelar/', views.OrdemServicoCancelarView.as_view()),
    path('ordens/<uuid:pk>/historico/', views.OrdemServicoHistoricoView.as_view()),
    path('ordens/delegacao/<uuid:delegacaoId>/', views.OrdemServicoPorDelegacaoView.as_view()),
]
