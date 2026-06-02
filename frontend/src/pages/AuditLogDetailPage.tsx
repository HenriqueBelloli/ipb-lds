import { useEffect, useMemo, useState } from "react";
import { AuditLog, getAuditLog } from "../services/audit";
import { formatDateTime, formatService, shortenId } from "./AuditLogsPage";

type AuditLogDetailPageProps = {
  log: AuditLog;
  onBack: () => void;
};

export function AuditLogDetailPage({ log, onBack }: AuditLogDetailPageProps) {
  const [auditLog, setAuditLog] = useState(log);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let isCurrent = true;

    async function loadDetail() {
      setIsLoading(true);
      setError(null);

      try {
        const detail = await getAuditLog(log.id);
        if (isCurrent) {
          setAuditLog(detail);
        }
      } catch (loadError) {
        if (isCurrent) {
          setError(loadError instanceof Error ? loadError.message : "Não foi possível carregar o detalhe do log.");
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    loadDetail();

    return () => {
      isCurrent = false;
    };
  }, [log.id]);

  const payloadText = useMemo(() => JSON.stringify(auditLog.payload, null, 2), [auditLog.payload]);

  return (
    <section className="audit-detail-page">
      <nav className="detail-breadcrumb" aria-label="Navegação">
        <button type="button" onClick={onBack}>Auditoria</button>
        <span>›</span>
        <strong>{auditLog.evento}</strong>
      </nav>

      <header className="detail-hero audit-detail-hero">
        <div>
          <h2>{auditLog.evento}</h2>
          <p>
            Registado em {formatDateTime(auditLog.timestamp)} · {formatService(auditLog.servico)}
          </p>
        </div>

        <span className={`detail-status ${getDetailStatusClass(auditLog.evento)}`}>
          <span aria-hidden="true">◆</span>
          Log imutável
        </span>

        <div className="detail-actions">
          <button className="detail-button detail-button-neutral" type="button" onClick={onBack}>
            Voltar
          </button>
        </div>
      </header>

      {error && (
        <aside className="client-alert audit-warning">
          <span aria-hidden="true">!</span>
          <div>
            <strong>Detalhe remoto indisponível</strong>
            <p>{error}. A mostrar os dados já carregados da listagem.</p>
          </div>
        </aside>
      )}

      <div className="audit-detail-grid">
        <section className="detail-card audit-info-card">
          <h3>Informações do Evento</h3>
          <div className="detail-divider" />

          <div className="info-grid">
            <InfoItem label="ID do Log">{auditLog.id}</InfoItem>
            <InfoItem label="Evento">{auditLog.evento}</InfoItem>
            <InfoItem label="Serviço">{formatService(auditLog.servico)}</InfoItem>
            <InfoItem label="Timestamp">{formatDateTime(auditLog.timestamp)}</InfoItem>
            <InfoItem label="Utilizador">{auditLog.usuarioId ?? "Não identificado"}</InfoItem>
            <InfoItem label="Delegação">{auditLog.delegacaoId ?? "Não identificada"}</InfoItem>
          </div>
        </section>

        <section className="detail-card audit-context-card">
          <h3>Contexto</h3>
          <div className="detail-divider" />

          <dl className="finance-summary">
            <div><dt>Serviço de origem</dt><dd>{auditLog.servico}</dd></div>
            <div><dt>Utilizador</dt><dd>{shortenId(auditLog.usuarioId)}</dd></div>
            <div><dt>Delegação</dt><dd>{shortenId(auditLog.delegacaoId)}</dd></div>
            <div className="finance-total"><dt>Estado</dt><dd>{isLoading ? "A actualizar" : "Carregado"}</dd></div>
          </dl>
        </section>

        <section className="detail-card audit-payload-card">
          <h3>Payload</h3>
          <div className="detail-divider" />
          <pre>{payloadText}</pre>
        </section>
      </div>
    </section>
  );
}

function InfoItem({ children, label }: { children: string; label: string }) {
  return (
    <div className="info-item">
      <span>{label}</span>
      <div>{children}</div>
    </div>
  );
}

function getDetailStatusClass(evento: string) {
  const normalizedEvent = evento.toLowerCase();

  if (normalizedEvent.includes("failed") || normalizedEvent.includes("erro") || normalizedEvent.includes("cancel")) {
    return "detail-status-canceled";
  }

  if (normalizedEvent.includes("success") || normalizedEvent.includes("criado") || normalizedEvent.includes("pago")) {
    return "detail-status-done";
  }

  return "detail-status-running";
}
