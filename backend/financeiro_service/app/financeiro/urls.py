from django.urls import path

from .views import (
    ContasReceberListView,
    ContasReceberDetailView,
    ContasReceberFaturarView,
    ClienteInadimplenteView,
    VerificarEntradaPagaView,
    VerificarPagamentosOSView,
    RegistrarPagamentoView,
    PagamentoDetailView,
    MensalidadeDetailPutView
)

urlpatterns = [
    #contas a receber
    path('financeiro/contas-receber/', ContasReceberListView.as_view(), name='contas-list'),
    path('financeiro/contas-receber/<uuid:pk>/', ContasReceberDetailView.as_view()),
    path('financeiro/contas-receber/<uuid:pk>/faturar/', ContasReceberFaturarView.as_view()),
    path('financeiro/contas-receber/entrada-paga/<uuid:osId>/', VerificarEntradaPagaView.as_view()),

    #clientes
    path('financeiro/clientes/<uuid:clienteId>/inadimplente/',ClienteInadimplenteView.as_view()),


    #pagamentos
    path('financeiro/pagamentos/os/<uuid:osId>/', VerificarPagamentosOSView.as_view()),
    path('financeiro/pagamentos/', RegistrarPagamentoView.as_view()),
    path('financeiro/pagamentos/<uuid:pagamentoId>/', PagamentoDetailView.as_view()),

    #mensalidade
    path('financeiro/mensalidades/configuracao/', MensalidadeDetailPutView.as_view()),


]