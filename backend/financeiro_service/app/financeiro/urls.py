from django.urls import path

from .views import (
    ContasReceberListView
)

urlpatterns = [
    #contas a receber
    path('financeiro/contas-receber/', ContasReceberListView.as_view(), name='contas-list')
]