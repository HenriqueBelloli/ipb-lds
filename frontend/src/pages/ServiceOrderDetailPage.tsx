import { ReactNode, useEffect, useState } from "react";
import { CheckIcon, ClipboardIcon, FileIcon, PencilIcon, SpinnerIcon } from "../shared/icons";
import {
  getServiceOrder,
  listServiceOrderHistory,
  listServiceOrderReceivables,
  ServiceOrder,
  ServiceOrderHistoryItem,
  ServiceOrderReceivable,
  ServiceOrderStatus,
} from "../services/serviceOrders";

type ServiceOrderDetailPageProps = {
  order: ServiceOrder;
  onBack: () => void;
};

const quickActions = [
  { label: "Ver duplicatas associadas", icon: ClipboardIcon },
  { label: "Exportar OS em PDF", icon: FileIcon },
  { label: "Alterar tecnico responsavel", icon: SpinnerIcon },
  { label: "Registar tempo de execucao", icon: SpinnerIcon },
];

const statusToneByName: Record<ServiceOrderStatus, string> = {
  ORCAMENTO: "neutral",
  AGUARDA_APROVACAO: "neutral",
  PAGAMENTO_PENDENTE: "running",
  A_EXECUTAR: "running",
  EM_EXECUCAO: "progress",
  CONCLUIDO: "done",
  FATURADO: "done",
  CANCELADO: "canceled",
};

export function ServiceOrderDetailPage({ order, onBack }: ServiceOrderDetailPageProps) {
  const [detailOrder, setDetailOrder] = useState<ServiceOrder>(order);
  const [historyItems, setHistoryItems] = useState<ServiceOrderHistoryItem[]>([]);
  const [receivables, setReceivables] = useState<ServiceOrderReceivable[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const currentTone = statusToneByName[detailOrder.status];
  const paidAmount = receivables.reduce((total, receivable) => total + receivable.paidValue, 0);
  const receivableAmount = receivables.reduce((total, receivable) => total + Math.max(receivable.value - receivable.paidValue, 0), 0);
  const entryReceivable = receivables.find((receivable) => receivable.type === "ENTRADA");

  useEffect(() => {
    let isMounted = true;

    async function loadDetail() {
      try {
        setIsLoading(true);
        setError(null);

        const [nextOrder, nextHistory, nextReceivables] = await Promise.all([
          getServiceOrder(order.id),
          listServiceOrderHistory(order.id),
          listServiceOrderReceivables(order.id),
        ]);

        if (isMounted) {
          setDetailOrder(nextOrder);
          setHistoryItems(nextHistory);
          setReceivables(nextReceivables);
        }
      } catch (loadError) {
        if (isMounted) {
          setError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar a ordem de servico.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadDetail();

    return () => {
      isMounted = false;
    };
  }, [order.id]);

  return (
    <section className="order-detail-page" data-node-id="17:806">
      <nav className="detail-breadcrumb" aria-label="Navegacao">
        <button type="button" onClick={onBack}>
          Ordens de Servico
        </button>
        <span>&rsaquo;</span>
        <strong>{detailOrder.number}</strong>
      </nav>

      {error ? <div className="orders-message orders-message-error">{error}</div> : null}
      {isLoading ? <div className="orders-message">A carregar detalhe da ordem de servico...</div> : null}

      <header className="detail-hero">
        <div>
          <h2>{detailOrder.number}</h2>
          <p>
            Criada em {detailOrder.date} por {detailOrder.createdBy}
          </p>
        </div>

        <span className={`detail-status detail-status-${currentTone}`}>
          <span aria-hidden="true">*</span>
          {detailOrder.statusLabel}
        </span>

        <div className="detail-actions">
          <button className="detail-button detail-button-success" type="button">
            <CheckIcon aria-hidden="true" />
            Concluir OS
          </button>
          <button className="detail-button detail-button-danger" type="button">
            <span aria-hidden="true">x</span>
            Cancelar OS
          </button>
          <button className="detail-button detail-button-neutral" type="button">
            <PencilIcon aria-hidden="true" />
            Editar
          </button>
        </div>
      </header>

      <div className="detail-grid">
        <section className="detail-card detail-info-card">
          <h3>Informacoes da OS</h3>
          <div className="detail-divider" />

          <div className="info-grid">
            <InfoItem label="Cliente">
              <button className="text-link" type="button">
                {detailOrder.client}
              </button>
              <small>
                NIF {detailOrder.clientNif} - {detailOrder.clientMeta}
              </small>
            </InfoItem>
            <InfoItem label="Delegacao">{detailOrder.delegation}</InfoItem>
            <InfoItem label="Servico">{detailOrder.service}</InfoItem>
            <InfoItem label="Tipo de Preco">{formatPriceType(detailOrder.priceType)}</InfoItem>
            <InfoItem label="Data de Criacao">{detailOrder.date}</InfoItem>
            <InfoItem label="Ultima Atualizacao">{formatDateTime(detailOrder.updatedAt)}</InfoItem>
            <InfoItem label="Valor Recebido">
              <span className="inline-with-pill">
                {formatCurrency(paidAmount)}
                <span className={`mini-pill ${paidAmount > 0 ? "mini-pill-success" : "mini-pill-warning"}`}>
                  {paidAmount > 0 ? "Pago" : "Pendente"}
                </span>
              </span>
            </InfoItem>
            <InfoItem label="Valor Final">{detailOrder.amount}</InfoItem>
            <InfoItem className="info-wide" label="Saldo Restante">
              <strong className="amount-warning">{formatCurrency(receivableAmount)}</strong>
              <small>{receivables.length ? "Calculado pelas contas a receber" : "Sem contas a receber associadas"}</small>
            </InfoItem>
            <InfoItem className="info-full" label="Itens da OS">
              <div className="notes-box">
                {detailOrder.items.length ? (
                  detailOrder.items.map((item) => (
                    <p key={item.id}>
                      <strong>{item.serviceName}</strong>
                      {item.serviceDescription ? ` — ${item.serviceDescription}` : ""}
                      {" "}- {formatCurrency(item.appliedPrice)}
                      {item.bonified ? " - Bonificado" : ""}
                    </p>
                  ))
                ) : (
                  <p>Sem itens associados.</p>
                )}
              </div>
            </InfoItem>
            {detailOrder.cancellationReason ? (
              <InfoItem className="info-full" label="Motivo de Cancelamento">
                <p className="notes-box">{detailOrder.cancellationReason}</p>
              </InfoItem>
            ) : null}
          </div>
        </section>

        <section className="detail-card detail-history-card">
          <h3>Historico</h3>
          <div className="detail-divider" />

          <ol className="history-list">
            {historyItems.length ? (
              historyItems.map((item) => (
                <li className={`history-item history-${statusToneByName[item.nextStatus]}`} key={item.id}>
                  <strong>{item.statusLabel}</strong>
                  <span>{item.date}</span>
                  <span>por {item.actor}</span>
                  {item.observation && <p>{item.observation}</p>}
                </li>
              ))
            ) : (
              <li className="history-item history-muted">
                <strong>Sem historico</strong>
                <span>Ainda nao existem eventos registados.</span>
              </li>
            )}
          </ol>


        </section>

        <section className="detail-card detail-finance-card">
          <h3>Resumo Financeiro</h3>
          <div className="detail-divider" />

          <dl className="finance-summary">
            <div>
              <dt>Valor Total</dt>
              <dd>{detailOrder.amount}</dd>
            </div>
            <div>
              <dt>Entrada Recebida</dt>
              <dd className={entryReceivable && entryReceivable.paidValue > 0 ? "finance-success" : "finance-warning"}>
                <span className={`mini-pill ${entryReceivable && entryReceivable.paidValue > 0 ? "mini-pill-success" : "mini-pill-warning"}`}>
                  {entryReceivable ? entryReceivable.status : "Sem entrada"}
                </span>
                {formatCurrency(entryReceivable?.paidValue ?? 0)}
              </dd>
            </div>
            <div>
              <dt>Saldo a Receber</dt>
              <dd className="finance-warning">
                <span className="mini-pill mini-pill-warning">{receivableAmount > 0 ? "Pendente" : "Sem saldo"}</span>
                {formatCurrency(receivableAmount)}
              </dd>
            </div>
            <div className="finance-total">
              <dt>Estado do Pagamento</dt>
              <dd>{receivables.length ? summarizePaymentStatus(receivables) : "Sem contas associadas"}</dd>
            </div>
          </dl>
        </section>

        <section className="detail-card detail-quick-card">
          <h3>Accoes Rapidas</h3>
          <div className="detail-divider" />

          <div className="quick-actions">
            {quickActions.map((action) => {
              const Icon = action.icon;

              return (
                <button key={action.label} type="button">
                  <Icon aria-hidden="true" />
                  <span>{action.label}</span>
                  <strong aria-hidden="true">&rsaquo;</strong>
                </button>
              );
            })}
          </div>
        </section>
      </div>
    </section>
  );
}

function InfoItem({
  children,
  className = "",
  label,
}: {
  children: ReactNode;
  className?: string;
  label: string;
}) {
  return (
    <div className={`info-item ${className}`}>
      <span>{label}</span>
      <div>{children}</div>
    </div>
  );
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-PT", {
    style: "currency",
    currency: "EUR",
  }).format(Number.isFinite(value) ? value : 0);
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatPriceType(value: string) {
  return value === "ASSOCIADO" ? "Associado" : "Nao associado";
}

function summarizePaymentStatus(receivables: ServiceOrderReceivable[]) {
  if (receivables.every((receivable) => receivable.status === "PAGO")) {
    return "Pago";
  }

  if (receivables.some((receivable) => receivable.paidValue > 0)) {
    return "Parcialmente pago";
  }

  return "Pendente";
}
