import { FormEvent, useEffect, useMemo, useState } from "react";
import { EyeIcon } from "../shared/icons";
import {
  FinanceReceivable,
  FinanceReceivableFilters,
  ReceivableStatus,
  listFinanceReceivables,
  registerReceivablePayment,
} from "../services/finance";

const statusClass: Record<ReceivableStatus, string> = {
  ABERTA: "status-running",
  PARCIAL: "status-progress",
  PAGA: "status-done",
  VENCIDA: "status-canceled",
};

export function FinanceReceivablesPage() {
  const [receivables, setReceivables] = useState<FinanceReceivable[]>([]);
  const [filters, setFilters] = useState<FinanceReceivableFilters>({});
  const [draftFilters, setDraftFilters] = useState<FinanceReceivableFilters>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingPayment, setIsSavingPayment] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const metrics = useMemo(() => {
    const totals = receivables.reduce(
      (summary, receivable) => ({
        total: summary.total + receivable.amount,
        paid: summary.paid + receivable.paidAmount,
        open: summary.open + receivable.openAmount,
        overdue: summary.overdue + (receivable.status === "VENCIDA" ? receivable.openAmount : 0),
      }),
      { total: 0, paid: 0, open: 0, overdue: 0 },
    );

    return [
      { value: formatCurrency(totals.total), label: "Faturacao total emitida" },
      { value: formatCurrency(totals.paid), label: "Pagamentos recebidos", tone: "success" },
      { value: formatCurrency(totals.open), label: "Aguarda recebimento", tone: "warning" },
      { value: formatCurrency(totals.overdue), label: "Em atraso", tone: "danger" },
    ];
  }, [receivables]);

  const delegationOptions = useMemo(
    () => Array.from(new Set(receivables.map((receivable) => receivable.delegation).filter((delegation) => delegation !== "-"))).sort(),
    [receivables],
  );

  useEffect(() => {
    let isCurrent = true;

    async function loadReceivables() {
      setIsLoading(true);
      setError(null);

      try {
        const nextReceivables = await listFinanceReceivables(filters);

        if (isCurrent) {
          setReceivables(nextReceivables);
        }
      } catch (loadError) {
        if (isCurrent) {
          setReceivables([]);
          setError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar as contas a receber.");
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    void loadReceivables();

    return () => {
      isCurrent = false;
    };
  }, [filters]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFilters(draftFilters);
  }

  function handleReset() {
    setDraftFilters({});
    setFilters({});
  }

  async function handleReceive(receivable: FinanceReceivable) {
    const input = window.prompt("Valor recebido", receivable.openAmount.toFixed(2));

    if (!input) {
      return;
    }

    const value = Number(input.replace(",", "."));

    if (!Number.isFinite(value) || value <= 0) {
      setError("Informe um valor de pagamento valido.");
      return;
    }

    try {
      setIsSavingPayment(true);
      setError(null);
      await registerReceivablePayment(receivable.id, value);
      setFilters((current) => ({ ...current }));
    } catch (paymentError) {
      setError(paymentError instanceof Error ? paymentError.message : "Nao foi possivel registar o pagamento.");
    } finally {
      setIsSavingPayment(false);
    }
  }

  return (
    <section className="data-page" data-node-id="18:949">
      <div className="content-actions-row">
        <h2>Contas a Receber</h2>
        <div className="data-actions">
          <button className="secondary-action" type="button" onClick={() => setFilters({ ...filters })} disabled={isLoading}>
            Actualizar
          </button>
        </div>
      </div>

      <div className="summary-grid" aria-label="Resumo financeiro">
        {metrics.map((metric) => (
          <article className={`metric-card metric-${metric.tone ?? "default"}`} key={metric.label}>
            <strong>{metric.value}</strong>
            <span>{metric.label}</span>
          </article>
        ))}
      </div>

      <form className="data-filters finance-filters" aria-label="Filtros de duplicatas" onSubmit={handleSubmit} onReset={handleReset}>
        <select
          value={draftFilters.status ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, status: event.target.value as FinanceReceivableFilters["status"] }))}
        >
          <option value="">Todos os estados</option>
          <option value="ABERTA">Em aberto</option>
          <option value="PARCIAL">Parcial</option>
          <option value="PAGA">Paga</option>
          <option value="VENCIDA">Vencida</option>
        </select>
        <select
          value={draftFilters.type ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, type: event.target.value as FinanceReceivableFilters["type"] }))}
        >
          <option value="">Todos os tipos</option>
          <option value="ENTRADA">Entrada</option>
          <option value="SALDO_FINAL">Saldo final</option>
          <option value="MENSALIDADE">Mensalidade</option>
        </select>
        <select
          value={draftFilters.delegation ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, delegation: event.target.value }))}
        >
          <option value="">Todas as delegacoes</option>
          {delegationOptions.map((delegation) => <option key={delegation}>{delegation}</option>)}
        </select>
        <input
          aria-label="Pesquisar cliente"
          placeholder="Pesquisar cliente ou duplicata..."
          type="search"
          value={draftFilters.query ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, query: event.target.value }))}
        />
        <input
          aria-label="Data inicial"
          placeholder="De"
          type="date"
          value={draftFilters.dueDateFrom ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, dueDateFrom: event.target.value }))}
        />
        <input
          aria-label="Data final"
          placeholder="Ate"
          type="date"
          value={draftFilters.dueDateTo ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, dueDateTo: event.target.value }))}
        />
        <button className="filter-button" type="submit" disabled={isLoading}>Filtrar</button>
        <button className="clear-button" type="reset">Limpar</button>
      </form>

      {error ? <div className="login-alert login-alert-error">{error}</div> : null}

      <div className="data-table-card">
        <div className="data-table-wrap">
          <table className="data-table receivables-table">
            <thead>
              <tr>
                <th>No. Duplicata</th>
                <th>Cliente</th>
                <th>OS Origem</th>
                <th>Tipo</th>
                <th>Vencimento</th>
                <th className="amount-cell">Valor</th>
                <th>Estado</th>
                <th className="actions-cell">Accoes</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={8}>A carregar contas a receber...</td></tr>
              ) : receivables.map((item) => (
                <tr className={statusClass[item.status]} key={item.id}>
                  <td>{item.number}</td>
                  <td>{item.client}</td>
                  <td>{item.order}</td>
                  <td>{item.typeLabel}</td>
                  <td>{formatDate(item.dueDate)}</td>
                  <td className="amount-cell">{formatCurrency(item.amount)}</td>
                  <td><span className={`status-pill ${statusClass[item.status]}`}>{item.statusLabel}</span></td>
                  <td className="actions-cell">
                    {item.status === "PAGA" ? (
                      <button type="button" aria-label={`Ver ${item.number}`}><EyeIcon aria-hidden="true" /></button>
                    ) : (
                      <button className="receive-button" type="button" onClick={() => void handleReceive(item)} disabled={isSavingPayment}>
                        Receber
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <footer className="data-pagination">
          <span>{isLoading ? "A carregar duplicatas..." : `Mostrando ${receivables.length} duplicata${receivables.length === 1 ? "" : "s"}`}</span>
          <nav aria-label="Paginacao de duplicatas">
            <button type="button" disabled>&lt;</button>
            <button className="page-active" type="button">1</button>
            <button className="page-next" type="button" disabled>&gt;</button>
          </nav>
        </footer>
      </div>

      {!isLoading && !error && receivables.length === 0 ? (
        <div className="data-empty-state">
          <span className="empty-state-icon" aria-hidden="true">[]</span>
          <h3>Nenhuma conta a receber encontrada</h3>
          <p>Tente ajustar os filtros ou aguarde novas faturacoes do sistema.</p>
          <button className="clear-button" type="button" onClick={handleReset}>Limpar filtros</button>
        </div>
      ) : null}
    </section>
  );
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-PT", {
    style: "currency",
    currency: "EUR",
  }).format(Number.isFinite(value) ? value : 0);
}

function formatDate(value: string) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("pt-PT").format(new Date(value));
}
