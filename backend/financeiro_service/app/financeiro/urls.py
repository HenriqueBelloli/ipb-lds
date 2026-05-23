from django.urls import path

from .views import (
    ContasReceberListView,
    ContasReceberDetailView,
    ContasReceberFaturarView
)

urlpatterns = [
    #contas a receber
    path('financeiro/contas-receber/', ContasReceberListView.as_view(), name='contas-list'),
    path('financeiro/contas-receber/<uuid:pk>/', ContasReceberDetailView.as_view()),
    path('financeiro/contas-receber/<uuid:pk>/faturar/', ContasReceberFaturarView.as_view()),
]