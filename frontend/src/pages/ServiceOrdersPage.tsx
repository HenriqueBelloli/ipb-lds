import { EyeIcon } from "../shared/icons";

type OrderStatus = "A EXECUTAR" | "EM EXECUÇÃO" | "CONCLUÍDA" | "CANCELADA";

export type ServiceOrder = {
  number: string;
  client: string;
  service: string;
  delegation: string;
  status: OrderStatus;
  date: string;
  amount: string;
};

export const serviceOrders: ServiceOrder[] = [
  {
    number: "OS-2024-001",
    client: "Manuel Costa",
    service: "Análise de Solo",
    delegation: "Porto",
    status: "A EXECUTAR",
    date: "02/10/2024",
    amount: "€ 120,00",
  },
  {
    number: "OS-2024-002",
    client: "Ana Ferreira",
    service: "Trat. Fitossanitário",
    delegation: "Braga",
    status: "EM EXECUÇÃO",
    date: "28/09/2024",
    amount: "€ 350,00",
  },
  {
    number: "OS-2024-003",
    client: "João Rodrigues",
    service: "Análise de Água",
    delegation: "Porto",
    status: "CONCLUÍDA",
    date: "25/09/2024",
    amount: "€ 85,00",
  },
  {
    number: "OS-2024-004",
    client: "Maria Santos",
    service: "Consultoria Agrícola",
    delegation: "Aveiro",
    status: "CONCLUÍDA",
    date: "24/09/2024",
    amount: "€ 200,00",
  },
  {
    number: "OS-2024-005",
    client: "António Silva",
    service: "Análise de Solo",
    delegation: "Lisboa",
    status: "CANCELADA",
    date: "20/09/2024",
    amount: "€ 0,00",
  },
  {
    number: "OS-2024-006",
    client: "Carlos Oliveira",
    service: "Trat. Fitossanitário",
    delegation: "Coimbra",
    status: "A EXECUTAR",
    date: "18/09/2024",
    amount: "€ 350,00",
  },
  {
    number: "OS-2024-007",
    client: "Rosa Mendes",
    service: "Análise de Solo",
    delegation: "Braga",
    status: "EM EXECUÇÃO",
    date: "15/09/2024",
    amount: "€ 120,00",
  },
  {
    number: "OS-2024-008",
    client: "Francisco Lopes",
    service: "Consultoria Agrícola",
    delegation: "Porto",
    status: "CONCLUÍDA",
    date: "10/09/2024",
    amount: "€ 200,00",
  },
];

const statusClass: Record<OrderStatus, string> = {
  "A EXECUTAR": "status-running",
  "EM EXECUÇÃO": "status-progress",
  CONCLUÍDA: "status-done",
  CANCELADA: "status-canceled",
};

type ServiceOrdersPageProps = {
  onViewOrder: (order: ServiceOrder) => void;
};

export function ServiceOrdersPage({ onViewOrder }: ServiceOrdersPageProps) {
  return (
    <section className="orders-page" data-node-id="13:327">
      <div className="orders-title-row">
        <h2>Ordens de Serviço</h2>
        <button className="primary-action" type="button">
          <span aria-hidden="true">+</span>
          Nova OS
        </button>
      </div>

      <form className="orders-filters" aria-label="Filtros de ordens de serviço">
        <select defaultValue="">
          <option value="">Todos os estados</option>
          <option>A executar</option>
          <option>Em execução</option>
          <option>Concluída</option>
          <option>Cancelada</option>
        </select>
        <select defaultValue="">
          <option value="">Todas as delegações</option>
          <option>Porto</option>
          <option>Braga</option>
          <option>Aveiro</option>
          <option>Coimbra</option>
          <option>Lisboa</option>
        </select>
        <select defaultValue="">
          <option value="">Todos os serviços</option>
          <option>Análise de Solo</option>
          <option>Trat. Fitossanitário</option>
          <option>Análise de Água</option>
          <option>Consultoria Agrícola</option>
        </select>
        <input aria-label="Data inicial" placeholder="De" type="text" />
        <input aria-label="Data final" placeholder="Até" type="text" />
        <button className="filter-button" type="button">
          Filtrar
        </button>
        <button className="clear-button" type="reset">
          Limpar
        </button>
      </form>

      <div className="orders-table-card">
        <div className="orders-table-wrap">
          <table className="orders-table">
            <thead>
              <tr>
                <th>Nº OS</th>
                <th>Cliente</th>
                <th>Serviço</th>
                <th>Delegação</th>
                <th>Estado</th>
                <th>Data</th>
                <th className="amount-cell">Valor</th>
                <th className="actions-cell">Acções</th>
              </tr>
            </thead>
            <tbody>
              {serviceOrders.map((order) => (
                <tr
                  className={statusClass[order.status]}
                  key={order.number}
                  onDoubleClick={() => onViewOrder(order)}
                >
                  <td>{order.number}</td>
                  <td>{order.client}</td>
                  <td>{order.service}</td>
                  <td>{order.delegation}</td>
                  <td>
                    <span className={`status-pill ${statusClass[order.status]}`}>{order.status}</span>
                  </td>
                  <td>{order.date}</td>
                  <td className="amount-cell">{order.amount}</td>
                  <td className="actions-cell">
                    <button type="button" aria-label={`Ver ${order.number}`} onClick={() => onViewOrder(order)}>
                      <EyeIcon aria-hidden="true" />
                    </button>
                    <button type="button" aria-label={`Mais opções para ${order.number}`}>
                      <span aria-hidden="true">...</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <footer className="orders-pagination">
          <span>Mostrando 1–8 de 47 resultados</span>
          <nav aria-label="Paginação das ordens de serviço">
            <button type="button" disabled>
              ‹
            </button>
            <button className="page-active" type="button">
              1
            </button>
            <button type="button">2</button>
            <button type="button">3</button>
            <span>...</span>
            <button type="button">6</button>
            <button className="page-next" type="button">
              ›
            </button>
          </nav>
        </footer>
      </div>

      <div className="orders-empty-state">
        <span className="empty-state-label">Estado: Tabela Vazia</span>
        <span className="empty-state-icon" aria-hidden="true">
          ▣
        </span>
        <h3>Nenhuma ordem de serviço encontrada</h3>
        <p>Tente ajustar os filtros ou crie uma nova OS</p>
        <button className="clear-button" type="button">
          Nova OS
        </button>
      </div>
    </section>
  );
}
