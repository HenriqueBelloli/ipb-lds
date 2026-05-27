TRANSICOES_VALIDAS = {
    'ORCAMENTO':          ['AGUARDA_APROVACAO', 'CANCELADO'],
    'AGUARDA_APROVACAO':  ['PAGAMENTO_PENDENTE', 'A_EXECUTAR', 'CANCELADO'],
    'PAGAMENTO_PENDENTE': ['A_EXECUTAR', 'CANCELADO'],
    'A_EXECUTAR':         ['EM_EXECUCAO', 'CANCELADO'],
    'EM_EXECUCAO':        ['CONCLUIDO', 'CANCELADO'],
    'CONCLUIDO':          ['FATURADO'],
    'FATURADO':           [],
    'CANCELADO':          [],
}


def validar_transicao(status_atual: str, status_novo: str) -> bool:
    return status_novo in TRANSICOES_VALIDAS.get(status_atual, [])
