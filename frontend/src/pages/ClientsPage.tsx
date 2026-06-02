import { FormEvent, useEffect, useMemo, useState } from "react";
import { Client, ClientFilters, listClients } from "../services/clients";
import { EyeIcon, PencilIcon } from "../shared/icons";

type ClientsPageProps = {
  onEditClient: (client: Client) => void;
  onViewClient: (client: Client) => void;
};

export function ClientsPage({ onEditClient, onViewClient }: ClientsPageProps) {
  const [clients, setClients] = useState<Client[]>([]);
  const [filters, setFilters] = useState<ClientFilters>({ status: "" });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const delegationOptions = useMemo(
    () => Array.from(new Set(clients.flatMap((client) => client.delegations.map((delegation) => delegation.nome)))).sort(),
    [clients],
  );

  useEffect(() => {
    void loadClients();
  }, []);

  async function loadClients(nextFilters = filters) {
    try {
      setIsLoading(true);
      setError(null);
      setClients(await listClients(nextFilters));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar os clientes.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void loadClients();
  }

  function handleReset() {
    const emptyFilters: ClientFilters = { status: "" };
    setFilters(emptyFilters);
    void loadClients(emptyFilters);
  }

  return (
    <section className="data-page" data-node-id="22:1430">
      <div className="content-actions-row">
        <h2>Clientes</h2>
        <button className="primary-action" type="button"><span aria-hidden="true">+</span>Novo Cliente</button>
      </div>

      <form className="data-filters clients-filters" aria-label="Filtros de clientes" onSubmit={handleSubmit} onReset={handleReset}>
        <input
          aria-label="Pesquisar por nome ou NIF"
          placeholder="Pesquisar por nome ou NIF..."
          type="search"
          value={filters.query ?? ""}
          onChange={(event) => setFilters((current) => ({ ...current, query: event.target.value }))}
        />
        <select
          value={filters.delegation ?? ""}
          onChange={(event) => setFilters((current) => ({ ...current, delegation: event.target.value }))}
        >
          <option value="">Todas as delegacoes</option>
          {delegationOptions.map((delegation) => <option key={delegation}>{delegation}</option>)}
        </select>
        <select
          value={filters.status ?? ""}
          onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value as ClientFilters["status"] }))}
        >
          <option value="">Todos</option>
          <option value="active">Activos</option>
          <option value="inactive">Inactivos</option>
        </select>
        <label className="toggle-filter">
          <span>Apenas Inadimplentes</span>
          <input
            type="checkbox"
            checked={filters.delinquentOnly ?? false}
            onChange={(event) => setFilters((current) => ({ ...current, delinquentOnly: event.target.checked }))}
          />
          <i aria-hidden="true" />
        </label>
        <button className="filter-button" type="submit" disabled={isLoading}>Filtrar</button>
        <button className="clear-button" type="reset">Limpar</button>
      </form>

      {error ? <div className="login-alert login-alert-error">{error}</div> : null}

      <div className="data-table-card">
        <div className="data-table-wrap">
          <table className="data-table clients-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>NIF</th>
                <th>Delegacao</th>
                <th>Telefone</th>
                <th>Associado</th>
                <th>Estado</th>
                <th>Inadimplente</th>
                <th className="actions-cell">Accoes</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={8}>A carregar clientes...</td></tr>
              ) : clients.map((client) => (
                <tr
                  className={client.delinquent ? "client-delinquent-row" : ""}
                  key={client.id}
                  onDoubleClick={() => onViewClient(client)}
                >
                  <td>{client.name}</td>
                  <td>{client.nif}</td>
                  <td>{client.delegation}</td>
                  <td>{client.phone}</td>
                  <td>{client.associated ? "Sim" : "Nao"}</td>
                  <td><span className={`status-pill ${client.status === "Activo" ? "status-done" : "status-muted"}`}>{client.status}</span></td>
                  <td className={client.delinquent ? "danger-text" : ""}>{client.delinquent ? "! Sim" : "Nao"}</td>
                  <td className="actions-cell">
                    <button type="button" aria-label={`Ver ${client.name}`} title="Ver detalhes" onClick={() => onViewClient(client)}><EyeIcon aria-hidden="true" /></button>
                    <button type="button" aria-label={`Editar ${client.name}`} title="Editar" onClick={() => onEditClient(client)}><PencilIcon aria-hidden="true" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <footer className="data-pagination">
          <span>Mostrando {clients.length} cliente{clients.length === 1 ? "" : "s"}</span>
          <nav aria-label="Paginacao de clientes">
            <button type="button" disabled>&lt;</button>
            <button className="page-active" type="button">1</button>
            <button className="page-next" type="button" disabled>&gt;</button>
          </nav>
        </footer>
      </div>

      {!isLoading && !error && clients.length === 0 ? (
        <div className="data-empty-state">
          <span className="empty-state-icon" aria-hidden="true">[]</span>
          <h3>Nenhum cliente encontrado</h3>
          <p>Tente ajustar os filtros ou registe um novo cliente</p>
          <button className="clear-button" type="button">Novo Cliente</button>
        </div>
      ) : null}
    </section>
  );
}
