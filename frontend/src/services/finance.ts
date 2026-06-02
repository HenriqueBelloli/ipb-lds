import { Client, listClients } from "./clients";
import { fetchWithAuth } from "./auth";

const FINANCEIRO_API_BASE_URL = import.meta.env.VITE_FINANCEIRO_API_BASE_URL ?? "http://127.0.0.1:8006";

export type ReceivableStatus = "ABERTA" | "PARCIAL" | "PAGA" | "VENCIDA";
export type ReceivableType = "ENTRADA" | "SALDO_FINAL" | "MENSALIDADE";

export type FinanceReceivableFilters = {
  status?: "" | ReceivableStatus;
  type?: "" | ReceivableType;
  query?: string;
  delegation?: string;
  dueDateFrom?: string;
  dueDateTo?: string;
};

export type FinanceReceivable = {
  id: string;
  number: string;
  clientId: string;
  client: string;
  delegation: string;
  order: string;
  type: ReceivableType;
  typeLabel: string;
  dueDate: string;
  amount: number;
  paidAmount: number;
  openAmount: number;
  status: ReceivableStatus;
  statusLabel: string;
  createdAt: string;
};

type ContaReceberApi = {
  id: string;
  clienteId: string;
  ordemServicoId: string | null;
  tipo: ReceivableType;
  valor: string;
  valorPago: string;
  status: ReceivableStatus;
  dataVencimento: string;
  createdAt: string;
};

type PaginatedResponse<T> = {
  results: T[];
};

type ListResponse<T> = T[] | PaginatedResponse<T>;

const typeLabels: Record<ReceivableType, string> = {
  ENTRADA: "Entrada",
  SALDO_FINAL: "Saldo final",
  MENSALIDADE: "Mensalidade",
};

const statusLabels: Record<ReceivableStatus, string> = {
  ABERTA: "Em aberto",
  PARCIAL: "Parcial",
  PAGA: "Paga",
  VENCIDA: "Vencida",
};

export async function listFinanceReceivables(filters: FinanceReceivableFilters = {}): Promise<FinanceReceivable[]> {
  const query = new URLSearchParams();

  if (filters.status) {
    query.set("status", filters.status);
  }

  if (filters.type) {
    query.set("tipo", filters.type);
  }

  if (filters.dueDateFrom) {
    query.set("dataVencimentoDe", toBackendDate(filters.dueDateFrom));
  }

  if (filters.dueDateTo) {
    query.set("dataVencimentoAte", toBackendDate(filters.dueDateTo));
  }

  const [receivablesResponse, clients] = await Promise.all([
    requestFinance<ListResponse<ContaReceberApi>>(`/api/financeiro/contas-receber/${query.size ? `?${query}` : ""}`),
    listClients().catch(() => [] as Client[]),
  ]);
  const clientById = new Map(clients.map((client) => [client.id, client]));
  const normalizedQuery = normalizeSearch(filters.query);
  const normalizedDelegation = filters.delegation?.trim();

  return normalizeListResponse(receivablesResponse)
    .map((receivable) => toReceivable(receivable, clientById.get(receivable.clienteId)))
    .filter((receivable) => {
      const matchesQuery =
        !normalizedQuery ||
        normalizeSearch(receivable.client).includes(normalizedQuery) ||
        normalizeSearch(receivable.number).includes(normalizedQuery) ||
        normalizeSearch(receivable.order).includes(normalizedQuery);
      const matchesDelegation = !normalizedDelegation || receivable.delegation === normalizedDelegation;

      return matchesQuery && matchesDelegation;
    });
}

export async function registerReceivablePayment(receivableId: string, value: number): Promise<void> {
  await requestFinance(`/api/financeiro/contas-receber/${receivableId}/pagamentos/`, {
    method: "POST",
    body: JSON.stringify({
      valor: value.toFixed(2),
      referenciaBancaria: null,
    }),
  });
}

function toReceivable(receivable: ContaReceberApi, client?: Client): FinanceReceivable {
  const amount = Number(receivable.valor);
  const paidAmount = Number(receivable.valorPago);

  return {
    id: receivable.id,
    number: `DUP-${receivable.id.slice(0, 8).toUpperCase()}`,
    clientId: receivable.clienteId,
    client: client?.name ?? receivable.clienteId,
    delegation: client?.delegation ?? "-",
    order: receivable.ordemServicoId ? `OS-${receivable.ordemServicoId.slice(0, 8).toUpperCase()}` : "-",
    type: receivable.tipo,
    typeLabel: typeLabels[receivable.tipo] ?? receivable.tipo,
    dueDate: receivable.dataVencimento,
    amount,
    paidAmount,
    openAmount: Math.max(amount - paidAmount, 0),
    status: receivable.status,
    statusLabel: statusLabels[receivable.status] ?? receivable.status,
    createdAt: receivable.createdAt,
  };
}

async function requestFinance<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetchWithAuth(new URL(path, FINANCEIRO_API_BASE_URL), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Nao foi possivel carregar os dados financeiros."));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

function normalizeListResponse<T>(response: ListResponse<T>): T[] {
  return Array.isArray(response) ? response : response.results;
}

async function getErrorMessage(response: Response, fallbackMessage: string) {
  try {
    const data = (await response.json()) as { detail?: string; erro?: string; message?: string };
    return data.detail ?? data.erro ?? data.message ?? fallbackMessage;
  } catch {
    return fallbackMessage;
  }
}

function toBackendDate(value: string) {
  return value.replaceAll("-", "");
}

function normalizeSearch(value?: string) {
  return (value ?? "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}
