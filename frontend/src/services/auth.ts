import { AppUser } from "../App";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8001";
const USUARIO_API_BASE_URL = import.meta.env.VITE_USUARIO_API_BASE_URL ?? "http://127.0.0.1:8002";
const SESSION_STORAGE_KEY = "erp-associacao-session";

type LoginResponse = {
  access: string;
  refresh: string;
  usuarioId: string;
  delegacaoId: string;
  perfil: string;
};

type UserProfileResponse = {
  id: string;
  nome: string;
  email: string;
  perfil: string;
  delegacaoId: string | null;
};

export type AuthSession = {
  accessToken: string;
  refreshToken: string;
  user: AppUser;
};

let refreshPromise: Promise<AuthSession> | null = null;

const delegationNames: Record<string, string> = {
  "10000000-0000-0000-0000-000000000001": "Delegação Sede",
  "10000000-0000-0000-0000-000000000002": "Delegação Norte",
};

const roleNames: Record<string, string> = {
  ADMINISTRADOR: "Administrador",
  DIRECAO: "Direção",
  FINANCEIRO: "Financeiro",
  GESTOR: "Gestor",
  OPERADOR: "Operador",
};

export async function loginWithBackend(email: string, password: string): Promise<AuthSession> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  const data = (await response.json()) as LoginResponse;
  let session = buildSession(email, data);
  persistSession(session);

  try {
    const profile = await fetchOwnProfile(session.accessToken, data.usuarioId);
    session = updateSessionUser(session, userFromProfile(session.user, profile));
  } catch {
    persistSession(session);
  }

  return session;
}

export async function logoutFromBackend(session: AuthSession | null): Promise<void> {
  if (!session) {
    clearSession();
    return;
  }

  try {
    await fetch(`${API_BASE_URL}/api/auth/logout/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh: session.refreshToken }),
    });
  } finally {
    clearSession();
  }
}

export async function fetchWithAuth(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  const session = getStoredSession();

  if (!session?.accessToken) {
    throw new Error("Sessão expirada. Inicie sessão novamente.");
  }

  const response = await fetch(input, withAuthHeaders(init, session.accessToken));

  if (response.status !== 401) {
    return response;
  }

  const refreshedSession = await refreshStoredSession(session);
  return fetch(input, withAuthHeaders(init, refreshedSession.accessToken));
}

export function getStoredSession(): AuthSession | null {
  const rawSession = window.localStorage.getItem(SESSION_STORAGE_KEY);

  if (!rawSession) {
    return null;
  }

  try {
    return JSON.parse(rawSession) as AuthSession;
  } catch {
    clearSession();
    return null;
  }
}

export function clearSession() {
  window.localStorage.removeItem(SESSION_STORAGE_KEY);
}

export function updateStoredUser(user: AppUser): AuthSession | null {
  const session = getStoredSession();

  if (!session) {
    return null;
  }

  const updatedSession = updateSessionUser(session, user);
  return updatedSession;
}

function persistSession(session: AuthSession) {
  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}

async function refreshStoredSession(session: AuthSession): Promise<AuthSession> {
  if (!session.refreshToken) {
    clearSession();
    throw new Error("Sessão expirada. Inicie sessão novamente.");
  }

  refreshPromise ??= refreshSession(session).finally(() => {
    refreshPromise = null;
  });

  return refreshPromise;
}

async function refreshSession(session: AuthSession): Promise<AuthSession> {
  const response = await fetch(`${API_BASE_URL}/api/auth/refresh/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ refresh: session.refreshToken }),
  });

  if (!response.ok) {
    clearSession();
    throw new Error("Sessão expirada. Inicie sessão novamente.");
  }

  const data = (await response.json()) as Pick<LoginResponse, "access" | "refresh">;
  const refreshedSession = {
    ...session,
    accessToken: data.access,
    refreshToken: data.refresh,
  };

  persistSession(refreshedSession);
  return refreshedSession;
}

function withAuthHeaders(init: RequestInit, accessToken: string): RequestInit {
  return {
    ...init,
    headers: {
      Accept: "application/json",
      ...headersToObject(init.headers),
      Authorization: `Bearer ${accessToken}`,
    },
  };
}

function headersToObject(headers: HeadersInit | undefined): Record<string, string> {
  if (!headers) {
    return {};
  }

  if (headers instanceof Headers) {
    return Object.fromEntries(headers.entries());
  }

  if (Array.isArray(headers)) {
    return Object.fromEntries(headers);
  }

  return headers;
}

function buildSession(email: string, data: LoginResponse): AuthSession {
  const normalizedEmail = email.toLowerCase().trim();
  const localPart = normalizedEmail.split("@")[0] || "utilizador";
  const displayName = toDisplayName(localPart);

  return {
    accessToken: data.access,
    refreshToken: data.refresh,
    user: {
      initials: getInitials(displayName),
      name: displayName,
      email: normalizedEmail,
      delegation: delegationNames[data.delegacaoId] ?? "Delegação",
      role: roleNames[data.perfil] ?? data.perfil,
      usuarioId: data.usuarioId,
      delegacaoId: data.delegacaoId,
      perfil: data.perfil,
    },
  };
}

function updateSessionUser(session: AuthSession, user: AppUser): AuthSession {
  const updatedSession = {
    ...session,
    user,
  };

  persistSession(updatedSession);
  return updatedSession;
}

async function fetchOwnProfile(accessToken: string, usuarioId: string): Promise<UserProfileResponse> {
  const response = await fetchUserProfile(accessToken, "/api/usuarios/me/");

  if (response.ok) {
    return response.json() as Promise<UserProfileResponse>;
  }

  if (response.status === 404) {
    const fallbackResponse = await fetchUserProfile(accessToken, `/api/usuarios/${usuarioId}/`);

    if (fallbackResponse.ok) {
      return fallbackResponse.json() as Promise<UserProfileResponse>;
    }
  }

  throw new Error("Nao foi possivel carregar o perfil.");
}

function fetchUserProfile(accessToken: string, path: string) {
  return fetch(new URL(path, USUARIO_API_BASE_URL), {
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

function userFromProfile(currentUser: AppUser, profile: UserProfileResponse): AppUser {
  const delegationId = profile.delegacaoId ?? currentUser.delegacaoId;

  return {
    ...currentUser,
    initials: getInitials(profile.nome),
    name: profile.nome,
    email: profile.email,
    delegation: delegationNames[delegationId] ?? currentUser.delegation,
    role: roleNames[profile.perfil] ?? profile.perfil,
    usuarioId: profile.id,
    delegacaoId: delegationId,
    perfil: profile.perfil,
  };
}

async function getErrorMessage(response: Response) {
  try {
    const data = (await response.json()) as { detail?: string; email?: string[]; password?: string[] };
    return data.detail ?? data.email?.[0] ?? data.password?.[0] ?? "Não foi possível iniciar sessão.";
  } catch {
    return "Não foi possível iniciar sessão.";
  }
}

function toDisplayName(value: string) {
  return value
    .replace(/[._-]+/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function getInitials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");
}
