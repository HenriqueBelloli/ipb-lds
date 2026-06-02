import { fetchWithAuth } from "./auth";

const CLIENTE_API_BASE_URL = import.meta.env.VITE_CLIENTE_API_BASE_URL ?? "http://127.0.0.1:8003";
const OS_API_BASE_URL = import.meta.env.VITE_OS_API_BASE_URL ?? "http://127.0.0.1:8005";
const SERVICO_API_BASE_URL = import.meta.env.VITE_SERVICO_API_BASE_URL ?? "http://127.0.0.1:8004";
const USUARIO_API_BASE_URL = import.meta.env.VITE_USUARIO_API_BASE_URL ?? "http://127.0.0.1:8002";
const FINANCEIRO_API_BASE_URL = import.meta.env.VITE_FINANCEIRO_API_BASE_URL ?? "http://127.0.0.1:8006";

export type ServiceOrderStatus =
  | "ORCAMENTO"
  | "AGUARDA_APROVACAO"
  | "PAGAMENTO_PENDENTE"
  | "A_EXECUTAR"
  | "EM_EXECUCAO"
  | "CONCLUIDO"
  | "FATURADO"
  | "CANCELADO";

export type ServiceOrderItem = {
  id: string;
  serviceId: string;
  serviceDelegationId: string;
  serviceName: string;
  serviceDescription: string | null;
  appliedPrice: number;
  entryPercent: number;
  bonified: boolean;
};

export type ServiceOrder = {
  id: string;
  number: string;
  clientId: string;
  client: string;
  clientNif: string;
  clientMeta: string;
  delegationId: string;
  delegation: string;
  createdById: string;
  createdBy: string;
  service: string;
  status: ServiceOrderStatus;
  statusLabel: string;
  date: string;
  createdAt: string;
  updatedAt: string;
  amount: string;
  amountValue: number;
  priceType: string;
  cancellationReason?: string | null;
  items: ServiceOrderItem[];
};

export type ServiceOrderHistoryItem = {
  id: string;
  userId: string | null;
  actor: string;
  previousStatus: ServiceOrderStatus | null;
  nextStatus: ServiceOrderStatus;
  statusLabel: string;
  observation: string;
  createdAt: string;
  date: string;
};

export type ServiceOrderReceivable = {
  id: string;
  type: string;
  value: number;
  paidValue: number;
  status: string;
  dueDate: string;
};

export type DelegationService = {
  id: string;
  serviceId: string;
  name: string;
  description: string | null;
  bonifiable: boolean;
  associatedPrice: number;
  nonAssociatedPrice: number;
  appliedPrice: number;
  entryPercent: number;
};

export type ServiceOrderCreateInput = {
  clientId: string;
  executionDelegationId: string;
  priceType: "ASSOCIADO" | "NAO_ASSOCIADO";
  items: Array<{
    serviceId: string;
    serviceDelegationId: string;
    appliedPrice: number;
    entryPercent: number;
    bonified: boolean;
  }>;
};

type OrdemServicoApi = {
  id: string;
  clienteId: string;
  delegacaoContratacaoId: string;
  delegacaoExecucaoId: string;
  usuarioCriacaoId: string;
  status: ServiceOrderStatus;
  valorTotal: string;
  tipoPreco: string;
  motivoCancelamento: string | null;
  createdAt: string;
  updatedAt: string;
  itens: OrdemServicoItemApi[];
};

type OrdemServicoItemApi = {
  id: string;
  servicoId: string;
  servicoDelegacaoId: string;
  precoAplicado: string;
  percentualEntrada: string;
  bonificado: boolean;
};

type OrdemServicoHistoricoApi = {
  id: string;
  usuarioId: string | null;
  statusAnterior: ServiceOrderStatus | null;
  statusNovo: ServiceOrderStatus;
  observacao: string | null;
  createdAt: string;
};

type ClienteApi = {
  id: string;
  nif: string;
  nome: string;
  flagAssociado: boolean;
};

type DelegacaoApi = {
  id: string;
  nome: string;
};

type ServicoApi = {
  id: string;
  nome: string;
  descricao: string | null;
};

type ServicoDelegacaoApi = {
  id: string;
  servicoId: string;
  nome: string;
  descricao: string | null;
  flagBonificavel: boolean;
  precoAssociado: string;
  precoNaoAssociado: string;
  precoAplicado: string | null;
  percentualEntrada: string;
};

type UsuarioApi = {
  id: string;
  nome: string;
};

type ContaReceberApi = {
  id: string;
  tipo: string;
  valor: string;
  valorPago: string;
  status: string;
  dataVencimento: string;
};

type PaginatedResponse<T> = {
  results: T[];
};

type ListResponse<T> = T[] | PaginatedResponse<T>;

const statusLabels: Record<ServiceOrderStatus, string> = {
  ORCAMENTO: "Orcamento",
  AGUARDA_APROVACAO: "Aguarda aprovacao",
  PAGAMENTO_PENDENTE: "Pagamento pendente",
  A_EXECUTAR: "A executar",
  EM_EXECUCAO: "Em execucao",
  CONCLUIDO: "Concluida",
  FATURADO: "Faturada",
  CANCELADO: "Cancelada",
};

export async function listServiceOrders(): Promise<ServiceOrder[]> {
  const [ordersResponse, clientes, delegacoes, servicos, usuarios] = await Promise.all([
    requestOs<ListResponse<OrdemServicoApi>>("/api/ordens/"),
    requestOptionalList<ClienteApi>(new URL("/api/clientes/", CLIENTE_API_BASE_URL)),
    requestOptionalList<DelegacaoApi>(new URL("/api/delegacoes/", USUARIO_API_BASE_URL)),
    requestOptionalList<ServicoApi>(new URL("/api/servicos/", SERVICO_API_BASE_URL)),
    requestOptionalList<UsuarioApi>(new URL("/api/usuarios/?ativo=true", USUARIO_API_BASE_URL)),
  ]);

  return normalizeListResponse(ordersResponse).map((order) => toServiceOrder(order, clientes, delegacoes, servicos, usuarios));
}

export async function getServiceOrder(id: string): Promise<ServiceOrder> {
  const order = await requestOs<OrdemServicoApi>(`/api/ordens/${id}/`);
  const [cliente, delegacoes, servicos, usuarios] = await Promise.all([
    requestOptional<ClienteApi | null>(new URL(`/api/clientes/${order.clienteId}/`, CLIENTE_API_BASE_URL), null),
    requestOptionalList<DelegacaoApi>(new URL("/api/delegacoes/", USUARIO_API_BASE_URL)),
    requestOptionalList<ServicoApi>(new URL("/api/servicos/", SERVICO_API_BASE_URL)),
    requestOptionalList<UsuarioApi>(new URL("/api/usuarios/?ativo=true", USUARIO_API_BASE_URL)),
  ]);

  return toServiceOrder(order, cliente ? [cliente] : [], delegacoes, servicos, usuarios);
}

export async function listDelegationServices(
  delegationId: string,
  priceType: "ASSOCIADO" | "NAO_ASSOCIADO",
): Promise<DelegationService[]> {
  const query = new URLSearchParams({
    ativo: "true",
    tipoPreco: priceType,
  });
  const services = await requestService<ListResponse<ServicoDelegacaoApi>>(`/api/servicos/delegacao/${delegationId}/?${query}`);

  return normalizeListResponse(services).map((service) => ({
    id: service.id,
    serviceId: service.servicoId,
    name: service.nome,
    description: service.descricao,
    bonifiable: service.flagBonificavel,
    associatedPrice: Number(service.precoAssociado),
    nonAssociatedPrice: Number(service.precoNaoAssociado),
    appliedPrice: Number(service.precoAplicado ?? (priceType === "ASSOCIADO" ? service.precoAssociado : service.precoNaoAssociado)),
    entryPercent: Number(service.percentualEntrada),
  }));
}

export async function createServiceOrder(input: ServiceOrderCreateInput): Promise<ServiceOrder> {
  const order = await requestOs<OrdemServicoApi>("/api/ordens/", {
    method: "POST",
    body: JSON.stringify({
      clienteId: input.clientId,
      delegacaoExecucaoId: input.executionDelegationId,
      tipoPreco: input.priceType,
      itens: input.items.map((item) => ({
        servicoId: item.serviceId,
        servicoDelegacaoId: item.serviceDelegationId,
        precoAplicado: item.appliedPrice.toFixed(2),
        percentualEntrada: item.entryPercent.toFixed(2),
        bonificado: item.bonified,
      })),
    }),
  });

  return getServiceOrder(order.id);
}

export async function updateServiceOrderStatus(
  orderId: string,
  status: ServiceOrderStatus,
  observation = "",
): Promise<ServiceOrder> {
  const order = await requestOs<OrdemServicoApi>(`/api/ordens/${orderId}/status/`, {
    method: "PATCH",
    body: JSON.stringify({
      status,
      observacao: observation,
    }),
  });

  return getServiceOrder(order.id);
}

export async function cancelServiceOrder(orderId: string, reason: string): Promise<ServiceOrder> {
  const order = await requestOs<OrdemServicoApi>(`/api/ordens/${orderId}/cancelar/`, {
    method: "PATCH",
    body: JSON.stringify({
      motivo: reason,
    }),
  });

  return getServiceOrder(order.id);
}

export async function listServiceOrderHistory(orderId: string): Promise<ServiceOrderHistoryItem[]> {
  const [historyResponse, usuarios] = await Promise.all([
    requestOs<ListResponse<OrdemServicoHistoricoApi>>(`/api/ordens/${orderId}/historico/`),
    requestOptionalList<UsuarioApi>(new URL("/api/usuarios/?ativo=true", USUARIO_API_BASE_URL)),
  ]);

  return normalizeListResponse(historyResponse).map((item) => ({
    id: item.id,
    userId: item.usuarioId,
    actor: usuarios.find((usuario) => usuario.id === item.usuarioId)?.nome ?? "Sistema",
    previousStatus: item.statusAnterior,
    nextStatus: item.statusNovo,
    statusLabel: formatStatus(item.statusNovo),
    observation: item.observacao ?? "",
    createdAt: item.createdAt,
    date: formatDateTime(item.createdAt),
  }));
}

export async function listServiceOrderReceivables(orderId: string): Promise<ServiceOrderReceivable[]> {
  const receivables = await requestOptionalList<ContaReceberApi>(
    new URL(`/api/financeiro/contas-receber/?ordemServicoId=${orderId}`, FINANCEIRO_API_BASE_URL),
  );

  return receivables.map((receivable) => ({
    id: receivable.id,
    type: receivable.tipo,
    value: Number(receivable.valor),
    paidValue: Number(receivable.valorPago),
    status: receivable.status,
    dueDate: receivable.dataVencimento,
  }));
}

export function formatStatus(status: ServiceOrderStatus) {
  return statusLabels[status] ?? status;
}

function toServiceOrder(
  order: OrdemServicoApi,
  clientes: ClienteApi[],
  delegacoes: DelegacaoApi[],
  servicos: ServicoApi[],
  usuarios: UsuarioApi[],
): ServiceOrder {
  const cliente = clientes.find((item) => item.id === order.clienteId);
  const delegacao = delegacoes.find((item) => item.id === order.delegacaoExecucaoId);
  const usuarioCriacao = usuarios.find((item) => item.id === order.usuarioCriacaoId);
  const items = order.itens.map((item) => toServiceOrderItem(item, servicos));
  const serviceNames = [...new Set(items.map((item) => item.serviceName))];

  return {
    id: order.id,
    number: `OS-${order.id.slice(0, 8).toUpperCase()}`,
    clientId: order.clienteId,
    client: cliente?.nome ?? order.clienteId,
    clientNif: cliente?.nif ?? "-",
    clientMeta: cliente ? `${cliente.flagAssociado ? "Associado" : "Nao associado"} - ${delegacao?.nome ?? "Delegacao nao identificada"}` : "-",
    delegationId: order.delegacaoExecucaoId,
    delegation: delegacao?.nome ?? order.delegacaoExecucaoId,
    createdById: order.usuarioCriacaoId,
    createdBy: usuarioCriacao?.nome ?? order.usuarioCriacaoId,
    service: serviceNames.length > 0 ? serviceNames.join(", ") : "Sem servicos",
    status: order.status,
    statusLabel: formatStatus(order.status),
    date: formatDate(order.createdAt),
    createdAt: order.createdAt,
    updatedAt: order.updatedAt,
    amount: formatCurrency(Number(order.valorTotal)),
    amountValue: Number(order.valorTotal),
    priceType: order.tipoPreco,
    cancellationReason: order.motivoCancelamento,
    items,
  };
}

function toServiceOrderItem(item: OrdemServicoItemApi, servicos: ServicoApi[]): ServiceOrderItem {
  const servico = servicos.find((service) => service.id === item.servicoId);

  return {
    id: item.id,
    serviceId: item.servicoId,
    serviceDelegationId: item.servicoDelegacaoId,
    serviceName: servico?.nome ?? item.servicoId,
    serviceDescription: servico?.descricao ?? null,
    appliedPrice: Number(item.precoAplicado),
    entryPercent: Number(item.percentualEntrada),
    bonified: item.bonificado,
  };
}

async function requestOs<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetchWithAuth(new URL(path, OS_API_BASE_URL), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Nao foi possivel carregar as ordens de servico."));
  }

  return response.json() as Promise<T>;
}

async function requestService<T>(path: string): Promise<T> {
  const response = await fetchWithAuth(new URL(path, SERVICO_API_BASE_URL), {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Nao foi possivel carregar os servicos."));
  }

  return response.json() as Promise<T>;
}

async function requestOptionalList<T>(url: URL): Promise<T[]> {
  const response = await requestOptional<ListResponse<T>>(url, []);
  return normalizeListResponse(response);
}

async function requestOptional<T>(url: URL, fallback: T): Promise<T> {
  try {
    const response = await fetchWithAuth(url);

    if (!response.ok) {
      return fallback;
    }

    return response.json() as Promise<T>;
  } catch {
    return fallback;
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

function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-PT", {
    style: "currency",
    currency: "EUR",
  }).format(Number.isFinite(value) ? value : 0);
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-PT").format(new Date(value));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}
