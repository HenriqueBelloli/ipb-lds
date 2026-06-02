import { fetchWithAuth } from "./auth";

const AUDIT_API_BASE_URL = import.meta.env.VITE_AUDITORIA_API_BASE_URL ?? "http://127.0.0.1:8008";

export type AuditLog = {
  id: string;
  evento: string;
  servico: string;
  usuarioId: string | null;
  delegacaoId: string | null;
  payload: unknown;
  timestamp: string;
};

export type AuditLogFilters = {
  evento?: string;
  servico?: string;
  usuarioId?: string;
  delegacaoId?: string;
  dataInicio?: string;
  dataFim?: string;
};

type PaginatedAuditResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: AuditLog[];
};

export type AuditLogListResult = {
  count: number;
  logs: AuditLog[];
};

export async function listAuditLogs(filters: AuditLogFilters = {}): Promise<AuditLogListResult> {
  const data = await requestAudit<AuditLog[] | PaginatedAuditResponse>(buildAuditUrl("/api/auditoria/", filters));

  if (Array.isArray(data)) {
    return { count: data.length, logs: data };
  }

  return { count: data.count, logs: data.results };
}

export async function getAuditLog(id: string): Promise<AuditLog> {
  return requestAudit<AuditLog>(buildAuditUrl(`/api/auditoria/${id}/`));
}

async function requestAudit<T>(url: string): Promise<T> {
  const response = await fetchWithAuth(url);

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json() as Promise<T>;
}

function buildAuditUrl(path: string, filters: AuditLogFilters = {}) {
  const url = new URL(path, AUDIT_API_BASE_URL);

  Object.entries(filters).forEach(([key, value]) => {
    const normalizedValue = value?.trim();
    if (normalizedValue) {
      url.searchParams.set(key, normalizedValue);
    }
  });

  return url.toString();
}

async function getErrorMessage(response: Response) {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail ?? "Não foi possível carregar os logs de auditoria.";
  } catch {
    return "Não foi possível carregar os logs de auditoria.";
  }
}
