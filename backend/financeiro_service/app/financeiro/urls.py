from django.urls import path

from .views import (
    ContasReceberListView,
    ContasReceberDetailView
)

urlpatterns = [
    #contas a receber
    path('financeiro/contas-receber/', ContasReceberListView.as_view(), name='contas-list'),
    path('financeiro/contas-receber/<uuid:pk>/', ContasReceberDetailView.as_view()),
]