import { useEffect, useState } from "react";
import { EyeIcon, PencilIcon } from "../shared/icons";
import { listServiceOrders, ServiceOrder, ServiceOrderStatus } from "../services/serviceOrders";

const statusClass: Record<ServiceOrderStatus, string> = {
  ORCAMENTO: "status-running",
  AGUARDA_APROVACAO: "status-running",
  PAGAMENTO_PENDENTE: "status-running",
  A_EXECUTAR: "status-running",
  EM_EXECUCAO: "status-progress",
  CONCLUIDO: "status-done",
  FATURADO: "status-done",
  CANCELADO: "status-canceled",
};

type ServiceOrdersPageProps = {
  onCreateOrder: () => void;
  onViewOrder: (order: ServiceOrder) => void;
};

export function ServiceOrdersPage({ onCreateOrder, onViewOrder }: ServiceOrdersPageProps) {
  const [serviceOrders, setServiceOrders] = useState<ServiceOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const hasOrders = serviceOrders.length > 0;

  useEffect(() => {
    let isMounted = true;

    async function loadOrders() {
      try {
        setIsLoading(true);
        setError(null);
        const orders = await listServiceOrders();

        if (isMounted) {
          setServiceOrders(orders);
        }
      } catch (loadError) {
        if (isMounted) {
          setError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar as ordens de servico.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadOrders();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <section className="orders-page" data-node-id="13:327">
      <div className="content-actions-row">
        <h2>Ordens de Servico</h2>
        <button className="primary-action" type="button" onClick={onCreateOrder}>
          <span aria-hidden="true">+</span>
          Nova OS
        </button>
      </div>

      <form className="orders-filters" aria-label="Filtros de ordens de servico">
        <select defaultValue="">
          <option value="">Todos os estados</option>
          <option value="ORCAMENTO">Orcamento</option>
          <option value="AGUARDA_APROVACAO">Aguarda aprovacao</option>
          <option value="PAGAMENTO_PENDENTE">Pagamento pendente</option>
          <option value="A_EXECUTAR">A executar</option>
          <option value="EM_EXECUCAO">Em execucao</option>
          <option value="CONCLUIDO">Concluida</option>
          <option value="FATURADO">Faturada</option>
          <option value="CANCELADO">Cancelada</option>
        </select>
        <select defaultValue="">
          <option value="">Todas as delegacoes</option>
          {[...new Set(serviceOrders.map((order) => order.delegation))]
            .filter(Boolean)
            .map((delegation) => (
              <option key={delegation}>{delegation}</option>
            ))}
        </select>
        <select defaultValue="">
          <option value="">Todos os servicos</option>
          {[...new Set(serviceOrders.map((order) => order.service))]
            .filter(Boolean)
            .map((service) => (
              <option key={service}>{service}</option>
            ))}
        </select>
        <input aria-label="Data inicial" placeholder="De" type="text" />
        <input aria-label="Data final" placeholder="Ate" type="text" />
        <button className="filter-button" type="button">
          Filtrar
        </button>
        <button className="clear-button" type="reset">
          Limpar
        </button>
      </form>

      <div className="orders-table-card">
        {error ? <div className="orders-message orders-message-error">{error}</div> : null}
        {isLoading ? <div className="orders-message">A carregar ordens de servico...</div> : null}

        <div className="orders-table-wrap">
          <table className="orders-table">
            <thead>
              <tr>
                <th>No OS</th>
                <th>Cliente</th>
                <th>Delegacao</th>
                <th>Estado</th>
                <th>Data</th>
                <th className="amount-cell">Valor</th>
                <th className="actions-cell">Accoes</th>
              </tr>
            </thead>
            <tbody>
              {!isLoading &&
                serviceOrders.map((order) => (
                  <tr
                    className={statusClass[order.status]}
                    key={order.id}
                    onDoubleClick={() => onViewOrder(order)}
                  >
                    <td>{order.number}</td>
                    <td>{order.client}</td>
                    <td>{order.delegation}</td>
                    <td>
                      <span className={`status-pill ${statusClass[order.status]}`}>{order.statusLabel}</span>
                    </td>
                    <td>{order.date}</td>
                    <td className="amount-cell">{order.amount}</td>
                    <td className="actions-cell">
                      <button
                        type="button"
                        aria-label={`Ver detalhes de ${order.number}`}
                        title="Ver detalhes"
                        onClick={() => onViewOrder(order)}
                      >
                        <EyeIcon aria-hidden="true" />
                      </button>
                      <button
                        type="button"
                        aria-label={`Editar ${order.number}`}
                        title="Editar"
                        onClick={() => onViewOrder(order)}
                      >
                        <PencilIcon aria-hidden="true" />
                      </button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>

        <footer className="orders-pagination">
          <span>{hasOrders ? `Mostrando ${serviceOrders.length} resultado(s)` : "Sem resultados"}</span>
          <nav aria-label="Paginacao das ordens de servico">
            <button type="button" disabled>
              &lsaquo;
            </button>
            <button className="page-active" type="button">
              1
            </button>
            <button className="page-next" type="button" disabled>
              &rsaquo;
            </button>
          </nav>
        </footer>
      </div>

      {!isLoading && !error && !hasOrders && (
        <div className="orders-empty-state">
          <span className="empty-state-label">Estado: Tabela Vazia</span>
          <span className="empty-state-icon" aria-hidden="true">
            []
          </span>
          <h3>Nenhuma ordem de servico encontrada</h3>
          <p>Tente ajustar os filtros para localizar uma OS existente.</p>
        </div>
      )}
    </section>
  );
}
