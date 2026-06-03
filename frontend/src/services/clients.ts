import { fetchWithAuth } from "./auth";

const CLIENTE_API_BASE_URL = import.meta.env.VITE_CLIENTE_API_BASE_URL ?? "http://127.0.0.1:8003";
const OS_API_BASE_URL = import.meta.env.VITE_OS_API_BASE_URL ?? "http://127.0.0.1:8005";
const FINANCEIRO_API_BASE_URL = import.meta.env.VITE_FINANCEIRO_API_BASE_URL ?? "http://127.0.0.1:8006";

export type Client = {
  id: string;
  name: string;
  initials: string;
  nif: string;
  delegation: string;
  delegations: ClientDelegation[];
  phone: string;
  email: string;
  address: string;
  associated: boolean;
  status: "Activo" | "Inactivo";
  delinquent: boolean;
  createdAt: string;
  priceType?: string;
};

export type ClientDelegation = {
  delegacaoId: string;
  nome: string;
};

export type ClientFilters = {
  query?: string;
  delegation?: string;
  status?: "" | "active" | "inactive";
  delinquentOnly?: boolean;
};

export type ClientServiceOrder = {
  id: string;
  status: string;
  date: string;
  amount: number;
  typePrice: string;
};

export type ClientReceivable = {
  id: string;
  value: number;
  paidValue: number;
  status: string;
  dueDate: string;
};

export type ClientUpdateInput = {
  nif: string;
  nome: string;
  telefone: string;
  email: string;
  morada: string;
  flagAssociado: boolean;
  ativo: boolean;
};

type ClienteApi = {
  id: string;
  nif: string;
  nome: string;
  telefone: string | null;
  email: string | null;
  morada: string | null;
  flagAssociado: boolean;
  ativo: boolean;
  createdAt: string;
  inadimplente?: boolean;
  tipoPreco?: string;
};

type OrdemServicoApi = {
  id: string;
  status: string;
  valorTotal: string;
  tipoPreco: string;
  createdAt: string;
};

type ContaReceberApi = {
  id: string;
  valor: string;
  valorPago: string;
  status: string;
  dataVencimento: string;
};

type ClienteInadimplenteApi = {
  inadimplente: boolean;
};

type PaginatedResponse<T> = {
  results: T[];
};

type ListResponse<T> = T[] | PaginatedResponse<T>;

export async function listClients(filters: ClientFilters = {}): Promise<Client[]> {
  const query = new URLSearchParams();
  const trimmedQuery = filters.query?.trim();

  if (trimmedQuery) {
    query.set(/^\d+$/.test(trimmedQuery) ? "nif" : "nome", trimmedQuery);
  }

  if (filters.status === "active") {
    query.set("ativo", "true");
  } else if (filters.status === "inactive") {
    query.set("ativo", "false");
  }

  const clientesResponse = await requestCliente<ListResponse<ClienteApi>>(`/api/clientes/${query.size ? `?${query}` : ""}`);
  const clientes = normalizeListResponse(clientesResponse);
  const clientsWithDelegations = await Promise.all(
    clientes.map(async (cliente) => {
      const [delegations, delinquent] = await Promise.all([
        safeListClientDelegations(cliente.id),
        safeGetClientDelinquent(cliente.id),
      ]);

      return toClient({ ...cliente, inadimplente: cliente.inadimplente ?? delinquent }, delegations);
    }),
  );

  return clientsWithDelegations.filter((client) => {
    const matchesDelegation = !filters.delegation || client.delegations.some((delegation) => delegation.nome === filters.delegation);
    const matchesDelinquent = !filters.delinquentOnly || client.delinquent;

    return matchesDelegation && matchesDelinquent;
  });
}

export async function getClient(id: string): Promise<Client> {
  const [cliente, delegations] = await Promise.all([requestCliente<ClienteApi>(`/api/clientes/${id}/`), safeListClientDelegations(id)]);
  return toClient(cliente, delegations);
}

export async function updateClient(id: string, input: ClientUpdateInput): Promise<Client> {
  await requestCliente<ClienteApi>(`/api/clientes/${id}/`, {
    method: "PUT",
    body: JSON.stringify(input),
  });

  return getClient(id);
}

export async function listClientServiceOrders(clientId: string): Promise<ClientServiceOrder[]> {
  const orders = normalizeListResponse(
    await requestOptional<ListResponse<OrdemServicoApi>>(new URL(`/api/ordens/?clienteId=${clientId}`, OS_API_BASE_URL)),
  );

  return orders.map((order) => ({
    id: order.id,
    status: order.status,
    date: order.createdAt,
    amount: Number(order.valorTotal),
    typePrice: order.tipoPreco,
  }));
}

export async function listClientReceivables(clientId: string): Promise<ClientReceivable[]> {
  const receivables = normalizeListResponse(
    await requestOptional<ListResponse<ContaReceberApi>>(
      new URL(`/api/financeiro/contas-receber/?clienteId=${clientId}`, FINANCEIRO_API_BASE_URL),
    ),
  );

  return receivables.map((receivable) => ({
    id: receivable.id,
    value: Number(receivable.valor),
    paidValue: Number(receivable.valorPago),
    status: receivable.status,
    dueDate: receivable.dataVencimento,
  }));
}

async function safeListClientDelegations(clientId: string): Promise<ClientDelegation[]> {
  return normalizeListResponse(
    await requestOptional<ListResponse<ClientDelegation>>(new URL(`/api/clientes/${clientId}/delegacoes/`, CLIENTE_API_BASE_URL)),
  );
}

async function safeGetClientDelinquent(clientId: string): Promise<boolean> {
  try {
    const response = await fetchWithAuth(new URL(`/api/financeiro/clientes/${clientId}/inadimplente/`, FINANCEIRO_API_BASE_URL));

    if (!response.ok) {
      return false;
    }

    const data = (await response.json()) as ClienteInadimplenteApi;
    return data.inadimplente;
  } catch {
    return false;
  }
}

function toClient(cliente: ClienteApi, delegations: ClientDelegation[]): Client {
  return {
    id: cliente.id,
    name: cliente.nome,
    initials: getInitials(cliente.nome),
    nif: cliente.nif,
    delegation: delegations[0]?.nome ?? "-",
    delegations,
    phone: cliente.telefone ?? "-",
    email: cliente.email ?? "-",
    address: cliente.morada ?? "-",
    associated: cliente.flagAssociado,
    status: cliente.ativo ? "Activo" : "Inactivo",
    delinquent: cliente.inadimplente ?? false,
    createdAt: cliente.createdAt,
    priceType: cliente.tipoPreco,
  };
}

async function requestCliente<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetchWithAuth(new URL(path, CLIENTE_API_BASE_URL), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Nao foi possivel carregar os clientes."));
  }

  return response.json() as Promise<T>;
}

async function requestOptional<T>(url: URL): Promise<T> {
  try {
    const response = await fetchWithAuth(url);

    if (!response.ok) {
      return [] as T;
    }

    return response.json() as Promise<T>;
  } catch {
    return [] as T;
  }
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

function getInitials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");
}
