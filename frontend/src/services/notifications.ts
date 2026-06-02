import { fetchWithAuth } from "./auth";

const NOTIFICATION_API_BASE_URL = import.meta.env.VITE_NOTIFICATION_API_BASE_URL ?? "http://127.0.0.1:8009";

export type Notification = {
  id: string;
  destinatarioId: string | null;
  tipoDestinatario: "USUARIO" | "CLIENTE" | "SISTEMA";
  canal: "INTERNO" | "EMAIL";
  titulo: string;
  mensagem: string;
  evento: string;
  payload: unknown;
  enviado: boolean;
  lida: boolean;
  erro: string | null;
  createdAt: string;
};

export async function listNotifications(): Promise<Notification[]> {
  return requestNotifications<Notification[]>("/api/notificacoes/");
}

export async function getNotification(id: string): Promise<Notification> {
  return requestNotifications<Notification>(`/api/notificacoes/${id}/`);
}

async function requestNotifications<T>(path: string): Promise<T> {
  const response = await fetchWithAuth(new URL(path, NOTIFICATION_API_BASE_URL));

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json() as Promise<T>;
}

async function getErrorMessage(response: Response) {
  try {
    const data = (await response.json()) as { detail?: string; message?: string };
    return data.detail ?? data.message ?? "Nao foi possivel carregar as notificacoes.";
  } catch {
    return "Nao foi possivel carregar as notificacoes.";
  }
}
