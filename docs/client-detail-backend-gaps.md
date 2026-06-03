# Levantamento de gaps - detalhe do cliente

O frontend passou a consumir as rotas existentes:

- `GET /api/clientes/`
- `GET /api/clientes/{id}/`
- `GET /api/clientes/{id}/delegacoes/`
- `GET /api/ordens/?clienteId={id}`
- `GET /api/financeiro/contas-receber/?clienteId={id}`

Para completar o detalhamento sem dados ficticios, ainda faltam estes dados/contratos:

1. `GET /api/clientes/{id}/` deve expor dados pessoais adicionais se forem necessarios na UI: data de nascimento, codigo postal, localidade, concelho, numero de associado, data de admissao, atualizadoEm e atualizadoPor.
2. A morada vem como texto unico (`morada`). Se a UI precisar de campos separados, criar campos estruturados ou um endpoint de endereco do cliente.
3. `GET /api/ordens/?clienteId={id}` retorna ids de servicos/delegacoes, mas nao nomes. Para o detalhe do cliente, adicionar nome/codigo da OS, nome do servico principal e nome da delegacao de execucao, ou criar endpoint agregado `GET /api/clientes/{id}/ordens/`.
4. `GET /api/financeiro/contas-receber/?clienteId={id}` depende de permissao financeira. Se operadores tambem devem ver resumo financeiro no detalhe do cliente, criar rota resumida para operador, por exemplo `GET /api/clientes/{id}/resumo-financeiro/`, com totalFaturado, totalPago, emAberto, vencido, quantidadeVencidas e diasMaiorAtraso.
5. A rota de inadimplencia atual (`GET /api/financeiro/clientes/{clienteId}/inadimplente/`) avalia apenas mensalidade do mes corrente. Confirmar se a regra de detalhe/listagem deve considerar todas as contas vencidas.
