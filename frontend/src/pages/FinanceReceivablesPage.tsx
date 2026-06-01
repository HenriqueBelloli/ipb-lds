import { EyeIcon } from "../shared/icons";

type ReceivableStatus = "EM ABERTO" | "PAGO" | "VENCIDO";

type Receivable = {
  number: string;
  client: string;
  order: string;
  type: string;
  dueDate: string;
  amount: string;
  status: ReceivableStatus;
};

const receivables: Receivable[] = [
  { number: "DUP-2024-001", client: "Manuel Costa", order: "OS-2024-001", type: "Entrada", dueDate: "05/10/2024", amount: "€36,00", status: "EM ABERTO" },
  { number: "DUP-2024-002", client: "Ana Ferreira", order: "OS-2024-002", type: "Entrada", dueDate: "02/10/2024", amount: "€105,00", status: "PAGO" },
  { number: "DUP-2024-003", client: "João Rodrigues", order: "OS-2024-003", type: "Saldo Final", dueDate: "30/09/2024", amount: "€76,50", status: "VENCIDO" },
  { number: "DUP-2024-004", client: "Maria Santos", order: "OS-2024-004", type: "Saldo Final", dueDate: "28/09/2024", amount: "€160,00", status: "PAGO" },
  { number: "DUP-2024-005", client: "Carlos Oliveira", order: "OS-2024-006", type: "Entrada", dueDate: "25/09/2024", amount: "€105,00", status: "VENCIDO" },
  { number: "DUP-2024-006", client: "Rosa Mendes", order: "OS-2024-007", type: "Mensalidade", dueDate: "01/10/2024", amount: "€45,00", status: "EM ABERTO" },
  { number: "DUP-2024-007", client: "Francisco Lopes", order: "OS-2024-008", type: "Saldo Final", dueDate: "15/09/2024", amount: "€160,00", status: "PAGO" },
  { number: "DUP-2024-008", client: "António Silva", order: "OS-2024-005", type: "Mensalidade", dueDate: "01/09/2024", amount: "€45,00", status: "VENCIDO" },
];

const statusClass: Record<ReceivableStatus, string> = {
  "EM ABERTO": "status-running",
  PAGO: "status-done",
  VENCIDO: "status-canceled",
};

const metrics = [
  { value: "€ 48.320,00", label: "Faturação total emitida" },
  { value: "€ 35.570,00", label: "Pagamentos recebidos", tone: "success" },
  { value: "€ 9.550,00", label: "Aguarda recebimento", tone: "warning" },
  { value: "€ 3.200,00", label: "Em atraso", tone: "danger" },
];

export function FinanceReceivablesPage() {
  return (
    <section className="data-page" data-node-id="18:949">
      <div className="data-title-row">
        <h2>Contas a Receber</h2>
        <div className="data-actions">
          <button className="secondary-action" type="button">Importar</button>
          <button className="primary-action" type="button">Exportar</button>
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

      <form className="data-filters finance-filters" aria-label="Filtros de duplicatas">
        <select defaultValue=""><option value="">Todos os estados</option><option>Em aberto</option><option>Pago</option><option>Vencido</option></select>
        <select defaultValue=""><option value="">Todos os tipos</option><option>Entrada</option><option>Saldo Final</option><option>Mensalidade</option></select>
        <select defaultValue=""><option value="">Todas as delegações</option><option>Porto</option><option>Braga</option><option>Lisboa</option></select>
        <input aria-label="Pesquisar cliente" placeholder="Pesquisar cliente..." type="search" />
        <input aria-label="Data inicial" placeholder="De" type="text" />
        <input aria-label="Data final" placeholder="Até" type="text" />
        <button className="filter-button" type="button">Filtrar</button>
      </form>

      <div className="data-table-card">
        <div className="data-table-wrap">
          <table className="data-table receivables-table">
            <thead>
              <tr>
                <th>Nº Duplicata</th>
                <th>Cliente</th>
                <th>OS Origem</th>
                <th>Tipo</th>
                <th>Vencimento</th>
                <th className="amount-cell">Valor</th>
                <th>Estado</th>
                <th className="actions-cell">Acções</th>
              </tr>
            </thead>
            <tbody>
              {receivables.map((item) => (
                <tr className={statusClass[item.status]} key={item.number}>
                  <td>{item.number}</td>
                  <td>{item.client}</td>
                  <td>{item.order}</td>
                  <td>{item.type}</td>
                  <td>{item.dueDate}</td>
                  <td className="amount-cell">{item.amount}</td>
                  <td><span className={`status-pill ${statusClass[item.status]}`}>{item.status}</span></td>
                  <td className="actions-cell">
                    {item.status === "PAGO" ? (
                      <button type="button" aria-label={`Ver ${item.number}`}><EyeIcon aria-hidden="true" /></button>
                    ) : (
                      <button className="receive-button" type="button">Receber</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <footer className="data-pagination">
          <span>Mostrando 1–8 de 34 duplicatas</span>
          <nav aria-label="Paginação de duplicatas">
            <button type="button" disabled>‹</button>
            <button className="page-active" type="button">1</button>
            <button type="button">2</button>
            <button type="button">3</button>
            <button type="button">4</button>
            <button className="page-next" type="button">›</button>
          </nav>
        </footer>
      </div>
    </section>
  );
}
