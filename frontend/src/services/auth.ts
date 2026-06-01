import { AppUser } from "../App";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8001";
const SESSION_STORAGE_KEY = "erp-associacao-session";

type LoginResponse = {
  access: string;
  refresh: string;
  usuarioId: string;
  delegacaoId: string;
  perfil: string;
};

export type AuthSession = {
  accessToken: string;
  refreshToken: string;
  user: AppUser;
};

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
  const session = buildSession(email, data);
  persistSession(session);
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

function persistSession(session: AuthSession) {
  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
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
