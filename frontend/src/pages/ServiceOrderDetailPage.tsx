import { ReactNode } from "react";
import { CheckIcon, ClipboardIcon, FileIcon, SpinnerIcon } from "../shared/icons";
import { ServiceOrder } from "./ServiceOrdersPage";

type ServiceOrderDetailPageProps = {
  order: ServiceOrder;
  onBack: () => void;
};

const detailByOrder: Record<string, Partial<ServiceOrderDetail>> = {
  "OS-2024-002": {
    createdBy: "João Silva",
    createdAt: "28/09/2024",
    nif: "234567890",
    clientMeta: "Associada · Porto",
    technician: "Pedro Alves",
    technicianInitials: "PA",
    expectedDate: "05/10/2024",
    entryPercent: "30%",
    entryAmount: "€ 105,00",
    remainingAmount: "€ 245,00",
    notes:
      "Cliente solicitou tratamento preventivo para pragas de Outono. Reagendar se chover na semana prevista.",
  },
};

type ServiceOrderDetail = {
  createdBy: string;
  createdAt: string;
  nif: string;
  clientMeta: string;
  technician: string;
  technicianInitials: string;
  expectedDate: string;
  entryPercent: string;
  entryAmount: string;
  remainingAmount: string;
  notes: string;
};

const defaultDetail: ServiceOrderDetail = {
  createdBy: "João Silva",
  createdAt: "28/09/2024",
  nif: "234567890",
  clientMeta: "Associada · Porto",
  technician: "Pedro Alves",
  technicianInitials: "PA",
  expectedDate: "05/10/2024",
  entryPercent: "30%",
  entryAmount: "€ 105,00",
  remainingAmount: "€ 245,00",
  notes: "Cliente solicitou acompanhamento técnico e atualização após execução no campo.",
};

const historyItems = [
  {
    status: "EM EXECUÇÃO",
    tone: "progress",
    date: "28/09/2024 às 14:32",
    actor: "por Pedro Alves",
    note: "Iniciada execução no campo",
  },
  {
    status: "APROVADA",
    tone: "running",
    date: "28/09/2024 às 09:15",
    actor: "por João Silva (Gestor)",
    note: "Entrada confirmada — € 105,00 recebidos",
  },
  {
    status: "PEND. APROVAÇÃO",
    tone: "neutral",
    date: "27/09/2024 às 16:48",
    actor: "por Maria Santos (Operador)",
    note: "",
  },
  {
    status: "CRIADA",
    tone: "muted",
    date: "27/09/2024 às 16:48",
    actor: "por Maria Santos (Operador)",
    note: "",
  },
];

const quickActions = [
  { label: "Ver duplicatas associadas", icon: ClipboardIcon },
  { label: "Exportar OS em PDF", icon: FileIcon },
  { label: "Alterar técnico responsável", icon: SpinnerIcon },
  { label: "Registar tempo de execução", icon: SpinnerIcon },
];

const statusToneByName = {
  "A EXECUTAR": "running",
  "EM EXECUÇÃO": "progress",
  CONCLUÍDA: "done",
  CANCELADA: "canceled",
};

export function ServiceOrderDetailPage({ order, onBack }: ServiceOrderDetailPageProps) {
  const detail = { ...defaultDetail, ...detailByOrder[order.number] };
  const currentTone = statusToneByName[order.status];

  return (
    <section className="order-detail-page" data-node-id="17:806">
      <nav className="detail-breadcrumb" aria-label="Navegação">
        <button type="button" onClick={onBack}>
          Ordens de Serviço
        </button>
        <span>›</span>
        <strong>{order.number}</strong>
      </nav>

      <header className="detail-hero">
        <div>
          <h2>{order.number}</h2>
          <p>
            Criada em {detail.createdAt} por {detail.createdBy}
          </p>
        </div>

        <span className={`detail-status detail-status-${currentTone}`}>
          <span aria-hidden="true">◷</span>
          {order.status}
        </span>

        <div className="detail-actions">
          <button className="detail-button detail-button-success" type="button">
            <CheckIcon aria-hidden="true" />
            Concluir OS
          </button>
          <button className="detail-button detail-button-danger" type="button">
            <span aria-hidden="true">×</span>
            Cancelar OS
          </button>
          <button className="detail-button detail-button-neutral" type="button">
            <span aria-hidden="true">✎</span>
            Editar
          </button>
        </div>
      </header>

      <div className="detail-grid">
        <section className="detail-card detail-info-card">
          <h3>Informações da OS</h3>
          <div className="detail-divider" />

          <div className="info-grid">
            <InfoItem label="Cliente">
              <button className="text-link" type="button">
                {order.client}
              </button>
              <small>
                NIF {detail.nif} · {detail.clientMeta}
              </small>
            </InfoItem>
            <InfoItem label="Delegação">{order.delegation}</InfoItem>
            <InfoItem label="Serviço">{order.service}</InfoItem>
            <InfoItem label="Técnico Responsável">
              <span className="technician">
                <span className="avatar avatar-small">{detail.technicianInitials}</span>
                {detail.technician}
              </span>
            </InfoItem>
            <InfoItem label="Data Prevista">
              <span className="inline-with-pill">
                {detail.expectedDate}
                <span className="mini-pill mini-pill-success">Dentro do prazo</span>
              </span>
            </InfoItem>
            <InfoItem label="Percentagem de Entrada">{detail.entryPercent}</InfoItem>
            <InfoItem label="Valor de Entrada">
              <span className="inline-with-pill">
                {detail.entryAmount}
                <span className="mini-pill mini-pill-success">Pago</span>
              </span>
            </InfoItem>
            <InfoItem label="Valor Final">{order.amount}</InfoItem>
            <InfoItem className="info-wide" label="Saldo Restante">
              <strong className="amount-warning">{detail.remainingAmount}</strong>
              <small>Aguarda conclusão da OS</small>
            </InfoItem>
            <InfoItem className="info-full" label="Observações">
              <p className="notes-box">{detail.notes}</p>
            </InfoItem>
          </div>
        </section>

        <section className="detail-card detail-history-card">
          <h3>Histórico</h3>
          <div className="detail-divider" />

          <ol className="history-list">
            {historyItems.map((item) => (
              <li className={`history-item history-${item.tone}`} key={`${item.status}-${item.date}`}>
                <strong>{item.status}</strong>
                <span>{item.date}</span>
                <span>{item.actor}</span>
                {item.note && <p>{item.note}</p>}
              </li>
            ))}
          </ol>

          <div className="history-note">
            <span aria-hidden="true">→</span>
            Aguarda conclusão para gerar saldo final
          </div>
        </section>

        <section className="detail-card detail-finance-card">
          <h3>Resumo Financeiro</h3>
          <div className="detail-divider" />

          <dl className="finance-summary">
            <div>
              <dt>Valor Total</dt>
              <dd>{order.amount}</dd>
            </div>
            <div>
              <dt>Entrada Recebida</dt>
              <dd className="finance-success">
                <span className="mini-pill mini-pill-success">Pago em 29/09/2024</span>
                {detail.entryAmount}
              </dd>
            </div>
            <div>
              <dt>Saldo a Receber</dt>
              <dd className="finance-warning">
                <span className="mini-pill mini-pill-warning">Aguarda conclusão</span>
                {detail.remainingAmount}
              </dd>
            </div>
            <div className="finance-total">
              <dt>Estado do Pagamento</dt>
              <dd>Parcialmente Pago</dd>
            </div>
          </dl>
        </section>

        <section className="detail-card detail-quick-card">
          <h3>Acções Rápidas</h3>
          <div className="detail-divider" />

          <div className="quick-actions">
            {quickActions.map((action) => {
              const Icon = action.icon;

              return (
                <button key={action.label} type="button">
                  <Icon aria-hidden="true" />
                  <span>{action.label}</span>
                  <strong aria-hidden="true">›</strong>
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
