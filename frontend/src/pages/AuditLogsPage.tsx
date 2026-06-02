import { FormEvent, useEffect, useMemo, useState } from "react";
import { EyeIcon } from "../shared/icons";
import { AuditLog, AuditLogFilters, listAuditLogs } from "../services/audit";

type AuditLogsPageProps = {
  onViewLog: (log: AuditLog) => void;
};

const serviceLabels: Record<string, string> = {
  auth: "Auth",
  cliente: "Clientes",
  financeiro: "Financeiro",
  os: "Ordens de Serviço",
  servico: "Serviços",
  usuario: "Utilizadores",
};

export function AuditLogsPage({ onViewLog }: AuditLogsPageProps) {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState<AuditLogFilters>({});
  const [draftFilters, setDraftFilters] = useState<AuditLogFilters>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;

    async function loadLogs() {
      setIsLoading(true);
      setError(null);

      try {
        const result = await listAuditLogs(filters);

        if (isCurrent) {
          setLogs(result.logs);
          setTotal(result.count);
        }
      } catch (loadError) {
        if (isCurrent) {
          setLogs([]);
          setTotal(0);
          setError(loadError instanceof Error ? loadError.message : "Não foi possível carregar os logs de auditoria.");
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    loadLogs();

    return () => {
      isCurrent = false;
    };
  }, [filters]);

  const summary = useMemo(() => {
    const failed = logs.filter((log) => log.evento.toLowerCase().includes("failed")).length;
    const services = new Set(logs.map((log) => log.servico)).size;
    const users = new Set(logs.map((log) => log.usuarioId).filter(Boolean)).size;

    return [
      { value: String(total), label: "Eventos registados" },
      { value: String(services), label: "Serviços envolvidos", tone: "success" },
      { value: String(users), label: "Utilizadores identificados", tone: "warning" },
      { value: String(failed), label: "Eventos críticos", tone: "danger" },
    ];
  }, [logs, total]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFilters(draftFilters);
  }

  function handleReset() {
    setDraftFilters({});
    setFilters({});
  }

  return (
    <section className="data-page audit-page">
      <div className="content-actions-row">
        <h2>Logs de Auditoria</h2>
        <button className="secondary-action" type="button" onClick={() => setFilters({ ...filters })}>
          Actualizar
        </button>
      </div>

      <div className="summary-grid" aria-label="Resumo de auditoria">
        {summary.map((metric) => (
          <article className={`metric-card metric-${metric.tone ?? "default"}`} key={metric.label}>
            <strong>{metric.value}</strong>
            <span>{metric.label}</span>
          </article>
        ))}
      </div>

      <form className="data-filters audit-filters" aria-label="Filtros de auditoria" onSubmit={handleSubmit}>
        <input
          aria-label="Filtrar por evento"
          placeholder="Evento"
          type="search"
          value={draftFilters.evento ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, evento: event.target.value }))}
        />
        <input
          aria-label="Filtrar por serviço"
          placeholder="Serviço"
          type="search"
          value={draftFilters.servico ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, servico: event.target.value }))}
        />
        <input
          aria-label="Filtrar por utilizador"
          placeholder="ID utilizador"
          type="search"
          value={draftFilters.usuarioId ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, usuarioId: event.target.value }))}
        />
        <input
          aria-label="Data inicial"
          placeholder="De"
          type="date"
          value={draftFilters.dataInicio ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, dataInicio: event.target.value }))}
        />
        <input
          aria-label="Data final"
          placeholder="Até"
          type="date"
          value={draftFilters.dataFim ?? ""}
          onChange={(event) => setDraftFilters((current) => ({ ...current, dataFim: event.target.value }))}
        />
        <button className="filter-button" type="submit">Filtrar</button>
        <button className="clear-button" type="button" onClick={handleReset}>Limpar</button>
      </form>

      <div className="data-table-card">
        <div className="data-table-wrap">
          <table className="data-table audit-table">
            <thead>
              <tr>
                <th>Evento</th>
                <th>Serviço</th>
                <th>Utilizador</th>
                <th>Delegação</th>
                <th>Data/Hora</th>
                <th>Payload</th>
                <th className="actions-cell">Acções</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr className={getEventTone(log.evento)} key={log.id} onDoubleClick={() => onViewLog(log)}>
                  <td><strong className="audit-event-name">{log.evento}</strong></td>
                  <td>{formatService(log.servico)}</td>
                  <td>{shortenId(log.usuarioId)}</td>
                  <td>{shortenId(log.delegacaoId)}</td>
                  <td>{formatDateTime(log.timestamp)}</td>
                  <td>{summarizePayload(log.payload)}</td>
                  <td className="actions-cell">
                    <button type="button" aria-label={`Ver log ${log.id}`} onClick={() => onViewLog(log)}>
                      <EyeIcon aria-hidden="true" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <footer className="data-pagination">
          <span>
            {isLoading
              ? "A carregar logs de auditoria..."
              : `Mostrando ${logs.length ? "1" : "0"}–${logs.length} de ${total} logs`}
          </span>
          <nav aria-label="Paginação de auditoria">
            <button type="button" disabled>‹</button>
            <button className="page-active" type="button">1</button>
            <button type="button" disabled>›</button>
          </nav>
        </footer>
      </div>

      {(error || (!isLoading && logs.length === 0)) && (
        <div className="data-empty-state">
          <span className="empty-state-icon" aria-hidden="true">▣</span>
          <h3>{error ? "Não foi possível carregar a auditoria" : "Nenhum log encontrado"}</h3>
          <p>{error ?? "Tente ajustar os filtros ou aguarde novos eventos do sistema."}</p>
          <button className="clear-button" type="button" onClick={() => setFilters({ ...filters })}>
            Tentar novamente
          </button>
        </div>
      )}
    </section>
  );
}

export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export function shortenId(value: string | null) {
  return value ? value.slice(0, 8) : "-";
}

export function formatService(value: string) {
  return serviceLabels[value] ?? value;
}

export function summarizePayload(payload: unknown) {
  if (!payload || typeof payload !== "object") {
    return String(payload ?? "-");
  }

  const entries = Object.entries(payload as Record<string, unknown>);
  if (!entries.length) {
    return "{}";
  }

  return entries
    .slice(0, 2)
    .map(([key, value]) => `${key}: ${String(value)}`)
    .join(" · ");
}

function getEventTone(evento: string) {
  const normalizedEvent = evento.toLowerCase();

  if (normalizedEvent.includes("failed") || normalizedEvent.includes("erro") || normalizedEvent.includes("cancel")) {
    return "status-canceled";
  }

  if (normalizedEvent.includes("success") || normalizedEvent.includes("criado") || normalizedEvent.includes("pago")) {
    return "status-done";
  }

  return "status-running";
}
