import { useEffect, useMemo, useState } from "react";
import {
  Client,
  ClientReceivable,
  ClientServiceOrder,
  getClient,
  listClientReceivables,
  listClientServiceOrders,
} from "../services/clients";
import { PencilIcon } from "../shared/icons";

type ClientDetailPageProps = {
  client: Client;
  onBack: () => void;
  canViewFinance: boolean;
  onEdit: (client: Client) => void;
};

export function ClientDetailPage({ client, canViewFinance, onBack, onEdit }: ClientDetailPageProps) {
  const [detail, setDetail] = useState<Client>(client);
  const [orders, setOrders] = useState<ClientServiceOrder[]>([]);
  const [receivables, setReceivables] = useState<ClientReceivable[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const finance = useMemo(() => summarizeReceivables(receivables), [receivables]);

  useEffect(() => {
    let isMounted = true;

    async function loadDetail() {
      try {
        setIsLoading(true);
        setError(null);
        const [nextDetail, nextOrders, nextReceivables] = await Promise.all([
          getClient(client.id),
          listClientServiceOrders(client.id),
          canViewFinance ? listClientReceivables(client.id) : Promise.resolve([]),
        ]);

        if (isMounted) {
          setDetail(nextDetail);
          setOrders(nextOrders);
          setReceivables(nextReceivables);
        }
      } catch (loadError) {
        if (isMounted) {
          setError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar o detalhe do cliente.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadDetail();

    return () => {
      isMounted = false;
    };
  }, [canViewFinance, client.id]);

  return (
    <section className="client-detail-page" data-node-id="23:1613">
      <nav className="detail-breadcrumb" aria-label="Navegacao">
        <button type="button" onClick={onBack}>Clientes</button>
        <span>&gt;</span>
        <strong>{detail.name}</strong>
      </nav>

      <header className="client-hero detail-card">
        <span className="avatar client-hero-avatar">{detail.initials}</span>
        <div>
          <h2>{detail.name}</h2>
          <p>NIF {detail.nif} - {detail.associated ? "Associado" : "Nao associado"} - {detail.delegation}</p>
        </div>
        <div className="client-badges">
          <span className="mini-pill mini-pill-success">OK {detail.status}</span>
          {detail.delinquent && <span className="mini-pill mini-pill-danger">! Inadimplente</span>}
        </div>
        <div className="detail-actions">
          <button className="detail-button detail-button-neutral" type="button" onClick={() => onEdit(detail)}>
            <PencilIcon aria-hidden="true" />
            Editar
          </button>
        </div>
      </header>

      {error ? <div className="login-alert login-alert-error">{error}</div> : null}
      {isLoading ? <div className="login-alert">A carregar detalhe do cliente...</div> : null}

      {canViewFinance && detail.delinquent && (
        <aside className="client-alert">
          <span aria-hidden="true">!</span>
          <div>
            <strong>Cliente com pagamentos em atraso</strong>
            <p>{finance.overdueCount} conta(s) vencida(s) - {formatCurrency(finance.overdue)} vencido</p>
          </div>
          <button className="clear-button" type="button">Ver Duplicatas</button>
        </aside>
      )}

      <div className="client-detail-grid">
        <div className="client-form-column">
          <section className="detail-card client-form-card">
            <header className="detail-card-header">
              <h3>Dados Pessoais</h3>
            </header>
            <div className="detail-divider" />
            <div className="form-grid">
              <Field label="Nome Completo" required value={detail.name} wide />
              <Field label="NIF" required value={detail.nif} />
              <Field label="Telefone" value={detail.phone} icon="Tel" />
              <Field label="Email" value={detail.email} icon="@" />
            </div>
          </section>

          <section className="detail-card client-form-card">
            <h3>Morada</h3>
            <div className="detail-divider" />
            <div className="form-grid">
              <Field label="Rua / Morada" value={detail.address} wide />
            </div>
          </section>

          <section className="detail-card client-form-card association-card">
            <h3>Dados de Associacao</h3>
            <div className="detail-divider" />
            <div className="form-grid">
              <Field label="Delegacao Principal" required value={detail.delegation} />
              <div className="field-block">
                <label>Delegacoes Adicionais</label>
                <div className="input-like tag-input">
                  {detail.delegations.length > 0 ? detail.delegations.map((delegation) => (
                    <span key={delegation.delegacaoId}>{delegation.nome}</span>
                  )) : <span>Nenhuma delegacao associada</span>}
                </div>
              </div>
            </div>
          </section>
        </div>

        <aside className="client-side-column">
          <section className="detail-card client-orders-card">
            <header className="detail-card-header">
              <h3>Ordens de Servico</h3>
              <span className="mini-pill mini-pill-info">{orders.length} OS</span>
            </header>
            <div className="detail-divider" />
            <div className="client-order-list">
              {orders.length === 0 ? <p>Nenhuma ordem de servico encontrada para este cliente.</p> : orders.map((order) => (
                <article className="client-order-item" key={order.id}>
                  <div>
                    <strong>OS {shortId(order.id)}</strong>
                    <span>{order.typePrice || "Servico nao detalhado na rota"}</span>
                    <small>{formatDate(order.date)}</small>
                  </div>
                  <span className={`status-pill ${statusClassForOrder(order.status)}`}>{formatStatus(order.status)}</span>
                </article>
              ))}
            </div>
            {orders.length > 0 ? <button className="side-link" type="button">Ver todas as OS</button> : null}
          </section>

          {canViewFinance ? (
            <section className="detail-card client-finance-card">
              <h3>Resumo Financeiro</h3>
              <div className="detail-divider" />
              <dl className="finance-summary">
                <div><dt>Total Faturado</dt><dd>{formatCurrency(finance.total)}</dd></div>
                <div><dt>Total Pago</dt><dd className="finance-success">{formatCurrency(finance.paid)}</dd></div>
                <div><dt>Em Aberto</dt><dd className="finance-warning">{formatCurrency(finance.open)}</dd></div>
                <div><dt>Vencido</dt><dd className="finance-warning">{formatCurrency(finance.overdue)}</dd></div>
                <div className="finance-total"><dt>Situacao Financeira</dt><dd className={detail.delinquent ? "finance-warning" : "finance-success"}>{detail.delinquent ? "Inadimplente" : "Regular"}</dd></div>
              </dl>
            </section>
          ) : null}
        </aside>
      </div>
    </section>
  );
}

function Field({
  icon,
  label,
  required = false,
  value,
  wide = false,
}: {
  icon?: string;
  label: string;
  required?: boolean;
  value: string;
  wide?: boolean;
}) {
  return (
    <div className={`field-block${wide ? " field-wide" : ""}`}>
      <label>{label}{required && <span> *</span>}</label>
      <div className="input-like">{icon && <i aria-hidden="true">{icon}</i>}<span>{value}</span></div>
    </div>
  );
}

function summarizeReceivables(receivables: ClientReceivable[]) {
  return receivables.reduce(
    (summary, receivable) => {
      const open = Math.max(receivable.value - receivable.paidValue, 0);
      const isOverdue = receivable.status === "VENCIDA";

      return {
        total: summary.total + receivable.value,
        paid: summary.paid + receivable.paidValue,
        open: summary.open + open,
        overdue: summary.overdue + (isOverdue ? open : 0),
        overdueCount: summary.overdueCount + (isOverdue ? 1 : 0),
      };
    },
    { total: 0, paid: 0, open: 0, overdue: 0, overdueCount: 0 },
  );
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR" }).format(value);
}

function formatDate(value: string) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("pt-PT").format(new Date(value));
}

function shortId(id: string) {
  return id.slice(0, 8).toUpperCase();
}

function statusClassForOrder(status: string) {
  const normalized = status.toUpperCase();

  if (normalized === "EM_EXECUCAO") {
    return "status-progress";
  }

  if (["CONCLUIDO", "FATURADO"].includes(normalized)) {
    return "status-done";
  }

  if (normalized === "CANCELADO") {
    return "status-canceled";
  }

  return "status-running";
}

function formatStatus(status: string) {
  return status.replaceAll("_", " ");
}
