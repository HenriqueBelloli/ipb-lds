import { fetchWithAuth, getStoredSession } from "./auth";

const AUTH_API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8001";
const USUARIO_API_BASE_URL = import.meta.env.VITE_USUARIO_API_BASE_URL ?? "http://127.0.0.1:8002";

export type UserProfile = "OPERADOR" | "GESTOR" | "FINANCEIRO" | "DIRECAO" | "ADMINISTRADOR";

export type ManagedUser = {
  id: string;
  nome: string;
  email: string;
  perfil: UserProfile;
  delegacaoId: string | null;
  ativo: boolean;
  createdAt: string;
};

export type Delegation = {
  id: string;
  codigo: string;
  nome: string;
  localizacao: string;
  responsavelId: string | null;
  ativo: boolean;
  createdAt: string;
};

export type UserCreateInput = {
  nome: string;
  email: string;
  password: string;
  perfil: UserProfile;
  delegacaoId: string;
};

export type UserUpdateInput = Omit<UserCreateInput, "password"> & {
  ativo: boolean;
};

export type UserProfileUpdateInput = {
  nome: string;
};

export type PasswordUpdateInput = {
  currentPassword: string;
  newPassword: string;
};

export type DelegationInput = {
  codigo: string;
  nome: string;
  localizacao: string;
  responsavelId: string | null;
  ativo: boolean;
};

export async function listUsers(): Promise<ManagedUser[]> {
  return requestManagement<ManagedUser[]>("/api/usuarios/?ativo=true");
}

export async function createUser(input: UserCreateInput): Promise<ManagedUser> {
  return requestManagement<ManagedUser>("/api/usuarios/", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function updateUser(id: string, input: UserUpdateInput): Promise<ManagedUser> {
  return requestManagement<ManagedUser>(`/api/usuarios/${id}/`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export async function updateOwnProfile(input: UserProfileUpdateInput): Promise<ManagedUser> {
  try {
    return await requestManagement<ManagedUser>("/api/usuarios/me/", {
      method: "PUT",
      body: JSON.stringify(input),
    });
  } catch (error) {
    if (!(error instanceof ApiRequestError) || error.status !== 404) {
      throw error;
    }

    const usuarioId = getStoredSession()?.user.usuarioId;

    if (!usuarioId) {
      throw new Error("Sessão expirada. Inicie sessão novamente.");
    }

    return requestManagement<ManagedUser>(`/api/usuarios/${usuarioId}/`, {
      method: "PUT",
      body: JSON.stringify(input),
    });
  }
}

export async function changeOwnPassword(input: PasswordUpdateInput): Promise<void> {
  await requestManagement<void>("/api/auth/password/", {
    baseUrl: AUTH_API_BASE_URL,
    method: "PUT",
    body: JSON.stringify(input),
    emptyResponse: true,
  });
}

export async function deleteUser(id: string, user: ManagedUser): Promise<ManagedUser> {
  return updateUser(id, {
    nome: user.nome,
    email: user.email,
    perfil: user.perfil,
    delegacaoId: user.delegacaoId ?? "",
    ativo: false,
  });
}

export async function listDelegations(): Promise<Delegation[]> {
  return requestManagement<Delegation[]>("/api/delegacoes/");
}

export async function createDelegation(input: DelegationInput): Promise<Delegation> {
  return requestManagement<Delegation>("/api/delegacoes/", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function updateDelegation(id: string, input: DelegationInput): Promise<Delegation> {
  return requestManagement<Delegation>(`/api/delegacoes/${id}/`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export async function deleteDelegation(id: string, delegation: Delegation): Promise<Delegation> {
  return updateDelegation(id, { ...toDelegationInput(delegation), ativo: false });
}

export function toDelegationInput(delegation: Delegation): DelegationInput {
  return {
    codigo: delegation.codigo,
    nome: delegation.nome,
    localizacao: delegation.localizacao,
    responsavelId: delegation.responsavelId,
    ativo: delegation.ativo,
  };
}

async function requestManagement<T>(
  path: string,
  init: RequestInit & { baseUrl?: string; emptyResponse?: boolean } = {},
): Promise<T> {
  const { baseUrl = USUARIO_API_BASE_URL, emptyResponse = false, ...requestInit } = init;
  const response = await fetchWithAuth(new URL(path, baseUrl), {
    ...requestInit,
    headers: {
      "Content-Type": "application/json",
      ...requestInit.headers,
    },
  });

  if (!response.ok) {
    throw new ApiRequestError(await getErrorMessage(response), response.status);
  }

  if (emptyResponse || response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

class ApiRequestError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "ApiRequestError";
  }
}

async function getErrorMessage(response: Response) {
  const fallbackMessage =
    response.status === 404
      ? "Rota não encontrada no serviço de usuários."
      : "Não foi possível concluir a operação.";

  try {
    const data = (await response.json()) as Record<string, string | string[]>;
    const firstValue = Object.values(data)[0];

    if (Array.isArray(firstValue)) {
      return firstValue[0] ?? fallbackMessage;
    }

    if (Array.isArray(data.detail)) {
      return data.detail[0] ?? fallbackMessage;
    }

    if (typeof data.detail === "string") {
      return data.detail;
    }

    return typeof firstValue === "string" ? firstValue : fallbackMessage;
  } catch {
    return fallbackMessage;
  }
}
