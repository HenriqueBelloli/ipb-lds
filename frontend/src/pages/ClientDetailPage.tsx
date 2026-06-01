import { CheckIcon } from "../shared/icons";
import { Client } from "./ClientsPage";

type ClientDetailPageProps = {
  client: Client;
  onBack: () => void;
};

const clientOrders = [
  { number: "OS-2024-002", service: "Tratamento Fitossanitário", date: "28/09/2024", status: "EM EXECUÇÃO", tone: "progress" },
  { number: "OS-2024-001", service: "Análise de Solo", date: "02/10/2024", status: "A EXECUTAR", tone: "running" },
  { number: "OS-2023-087", service: "Consultoria Agrícola", date: "15/06/2023", status: "CONCLUÍDA", tone: "done" },
  { number: "OS-2023-054", service: "Análise de Solo", date: "20/03/2023", status: "CONCLUÍDA", tone: "done" },
  { number: "OS-2022-112", service: "Análise de Água", date: "05/11/2022", status: "CONCLUÍDA", tone: "done" },
];

export function ClientDetailPage({ client, onBack }: ClientDetailPageProps) {
  const isAntónio = client.nif === "987654321";

  return (
    <section className="client-detail-page" data-node-id="23:1613">
      <nav className="detail-breadcrumb" aria-label="Navegação">
        <button type="button" onClick={onBack}>Clientes</button>
        <span>›</span>
        <strong>{client.name}</strong>
      </nav>

      <header className="client-hero detail-card">
        <span className="avatar client-hero-avatar">{client.initials}</span>
        <div>
          <h2>{client.name}</h2>
          <p>NIF {client.nif} · {client.associated ? "Associado" : "Não associado"} · {client.delegation}</p>
        </div>
        <div className="client-badges">
          <span className="mini-pill mini-pill-success">✓ {client.status}</span>
          {client.delinquent && <span className="mini-pill mini-pill-danger">⚠ Inadimplente</span>}
        </div>
        <div className="detail-actions">
          <button className="detail-button detail-button-neutral" type="button"><span aria-hidden="true">✎</span>Editar</button>
          <button className="detail-button detail-button-danger" type="button"><span aria-hidden="true">×</span>Desactivar Cliente</button>
        </div>
      </header>

      {client.delinquent && (
        <aside className="client-alert">
          <span aria-hidden="true">⚠</span>
          <div>
            <strong>Cliente com pagamentos em atraso</strong>
            <p>2 duplicatas vencidas · € 340,00 em aberto · há 45 dias</p>
          </div>
          <button className="clear-button" type="button">Ver Duplicatas</button>
        </aside>
      )}

      <div className="client-detail-grid">
        <div className="client-form-column">
          <section className="detail-card client-form-card">
            <header className="detail-card-header">
              <h3>Dados Pessoais</h3>
              <span className="mini-pill mini-pill-warning">A editar</span>
            </header>
            <div className="detail-divider" />
            <div className="form-grid">
              <Field label="Nome Completo" required value={client.name} wide />
              <Field label="NIF" required value={client.nif} />
              <Field label="Data de Nascimento" value={isAntónio ? "15/03/1975" : "10/05/1980"} />
              <Field label="Telefone" value={client.phone} icon="☎" />
              <Field label="Email" value={client.email} icon="✉" />
            </div>
          </section>

          <section className="detail-card client-form-card">
            <h3>Morada</h3>
            <div className="detail-divider" />
            <div className="form-grid">
              <Field label="Rua / Morada" value={isAntónio ? "Rua das Oliveiras, 42" : "Rua Principal, 18"} wide />
              <Field label="Código Postal" value={isAntónio ? "1200-456" : "4000-100"} />
              <Field label="Localidade" value={client.delegation} />
              <Field label="Concelho" value={client.delegation} />
            </div>
          </section>

          <section className="detail-card client-form-card association-card">
            <h3>Dados de Associação</h3>
            <div className="detail-divider" />
            <div className="form-grid">
              <Field label="Delegação Principal" required value={client.delegation} />
              <Field label="Nº de Associado" value={client.associated ? "ASS-2019-0342" : "-"} />
              <Field label="Data de Admissão" value="10/03/2019" />
              <div className="field-block">
                <label>Delegações Adicionais</label>
                <div className="input-like tag-input">
                  <span>Porto ×</span>
                  <span>Braga ×</span>
                  <button type="button">+ Adicionar delegação</button>
                </div>
              </div>
            </div>
          </section>
        </div>

        <aside className="client-side-column">
          <section className="detail-card client-orders-card">
            <header className="detail-card-header">
              <h3>Ordens de Serviço</h3>
              <span className="mini-pill mini-pill-info">5 OS</span>
            </header>
            <div className="detail-divider" />
            <div className="client-order-list">
              {clientOrders.map((order) => (
                <article className="client-order-item" key={order.number}>
                  <div>
                    <strong>{order.number}</strong>
                    <span>{order.service}</span>
                    <small>{order.date}</small>
                  </div>
                  <span className={`status-pill status-${order.tone}`}>{order.status}</span>
                </article>
              ))}
            </div>
            <button className="side-link" type="button">Ver todas as OS</button>
          </section>

          <section className="detail-card client-finance-card">
            <h3>Resumo Financeiro</h3>
            <div className="detail-divider" />
            <dl className="finance-summary">
              <div><dt>Total Faturado</dt><dd>€ 855,00</dd></div>
              <div><dt>Total Pago</dt><dd className="finance-success">€ 515,00</dd></div>
              <div><dt>Em Aberto</dt><dd className="finance-warning">€ 340,00</dd></div>
              <div><dt>Vencido</dt><dd className="finance-warning">€ 340,00</dd></div>
              <div className="finance-total"><dt>Situação Financeira</dt><dd className={client.delinquent ? "finance-warning" : "finance-success"}>{client.delinquent ? "Inadimplente" : "Regular"}</dd></div>
            </dl>
          </section>
        </aside>
      </div>

      <footer className="client-save-bar detail-card">
        <span>Última actualização: 01/10/2024 às 11:32 por João Silva</span>
        <div>
          <button className="detail-button detail-button-neutral" type="button">Cancelar</button>
          <button className="detail-button detail-button-success" type="button"><CheckIcon aria-hidden="true" />Guardar Alterações</button>
        </div>
      </footer>
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
