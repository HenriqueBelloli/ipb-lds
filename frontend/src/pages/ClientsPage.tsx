import { EyeIcon } from "../shared/icons";

export type Client = {
  name: string;
  initials: string;
  nif: string;
  delegation: string;
  phone: string;
  email: string;
  associated: boolean;
  status: "Activo" | "Inactivo";
  delinquent: boolean;
};

export const clients: Client[] = [
  { name: "Manuel Costa", initials: "MC", nif: "123456789", delegation: "Porto", phone: "912 345 678", email: "manuel.costa@email.pt", associated: true, status: "Activo", delinquent: false },
  { name: "Ana Ferreira", initials: "AF", nif: "234567890", delegation: "Braga", phone: "923 456 789", email: "ana.ferreira@email.pt", associated: true, status: "Activo", delinquent: false },
  { name: "António Silva", initials: "AS", nif: "987654321", delegation: "Lisboa", phone: "934 567 890", email: "antonio.silva@email.pt", associated: true, status: "Activo", delinquent: true },
  { name: "Maria Santos", initials: "MS", nif: "345678901", delegation: "Aveiro", phone: "945 678 901", email: "maria.santos@email.pt", associated: true, status: "Activo", delinquent: false },
  { name: "Carlos Oliveira", initials: "CO", nif: "456789012", delegation: "Coimbra", phone: "956 789 012", email: "carlos.oliveira@email.pt", associated: false, status: "Activo", delinquent: false },
  { name: "Rosa Mendes", initials: "RM", nif: "567890123", delegation: "Porto", phone: "967 890 123", email: "rosa.mendes@email.pt", associated: true, status: "Activo", delinquent: true },
  { name: "Francisco Lopes", initials: "FL", nif: "678901234", delegation: "Porto", phone: "978 901 234", email: "francisco.lopes@email.pt", associated: false, status: "Inactivo", delinquent: false },
  { name: "João Rodrigues", initials: "JR", nif: "789012345", delegation: "Porto", phone: "989 012 345", email: "joao.rodrigues@email.pt", associated: true, status: "Activo", delinquent: false },
];

type ClientsPageProps = {
  onViewClient: (client: Client) => void;
};

export function ClientsPage({ onViewClient }: ClientsPageProps) {
  return (
    <section className="data-page" data-node-id="22:1430">
      <div className="data-title-row">
        <h2>Clientes</h2>
        <button className="primary-action" type="button"><span aria-hidden="true">+</span>Novo Cliente</button>
      </div>

      <form className="data-filters clients-filters" aria-label="Filtros de clientes">
        <input aria-label="Pesquisar por nome ou NIF" placeholder="Pesquisar por nome ou NIF..." type="search" />
        <select defaultValue=""><option value="">Todas as delegações</option><option>Porto</option><option>Braga</option><option>Lisboa</option></select>
        <select defaultValue=""><option value="">Todos</option><option>Activos</option><option>Inactivos</option></select>
        <label className="toggle-filter">
          <span>Apenas Inadimplentes</span>
          <input type="checkbox" />
          <i aria-hidden="true" />
        </label>
        <button className="filter-button" type="button">Filtrar</button>
        <button className="clear-button" type="reset">Limpar</button>
      </form>

      <div className="data-table-card">
        <div className="data-table-wrap">
          <table className="data-table clients-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>NIF</th>
                <th>Delegação</th>
                <th>Telefone</th>
                <th>Associado</th>
                <th>Estado</th>
                <th>Inadimplente</th>
                <th className="actions-cell">Acções</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((client) => (
                <tr
                  className={client.delinquent ? "client-delinquent-row" : ""}
                  key={client.nif}
                  onDoubleClick={() => onViewClient(client)}
                >
                  <td>{client.name}</td>
                  <td>{client.nif}</td>
                  <td>{client.delegation}</td>
                  <td>{client.phone}</td>
                  <td>{client.associated ? "Sim" : "Não"}</td>
                  <td><span className={`status-pill ${client.status === "Activo" ? "status-done" : "status-muted"}`}>{client.status}</span></td>
                  <td className={client.delinquent ? "danger-text" : ""}>{client.delinquent ? "⚠ Sim" : "Não"}</td>
                  <td className="actions-cell">
                    <button type="button" aria-label={`Ver ${client.name}`} onClick={() => onViewClient(client)}><EyeIcon aria-hidden="true" /></button>
                    <button type="button" aria-label={`Editar ${client.name}`} onClick={() => onViewClient(client)}><span aria-hidden="true">✎</span></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <footer className="data-pagination">
          <span>Mostrando 1–8 de 156 clientes</span>
          <nav aria-label="Paginação de clientes">
            <button type="button" disabled>‹</button>
            <button className="page-active" type="button">1</button>
            <button type="button">2</button>
            <button type="button">3</button>
            <span>...</span>
            <button type="button">20</button>
            <button className="page-next" type="button">›</button>
          </nav>
        </footer>
      </div>

      <div className="data-empty-state">
        <span className="empty-state-icon" aria-hidden="true">▣</span>
        <h3>Nenhum cliente encontrado</h3>
        <p>Tente ajustar os filtros ou registe um novo cliente</p>
        <button className="clear-button" type="button">Novo Cliente</button>
      </div>
    </section>
  );
}
