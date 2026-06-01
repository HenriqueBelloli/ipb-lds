import { useState } from "react";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { AuthSession, getStoredSession, logoutFromBackend } from "./services/auth";

export type AppUser = {
  initials: string;
  name: string;
  email: string;
  delegation: string;
  role: string;
  usuarioId: string;
  delegacaoId: string;
  perfil: string;
};

export function App() {
  const [session, setSession] = useState<AuthSession | null>(() => getStoredSession());

  async function handleLogout() {
    const currentSession = session;
    setSession(null);
    await logoutFromBackend(currentSession);
  }

  if (session) {
    return <DashboardPage user={session.user} onLogout={handleLogout} />;
  }

  return <LoginPage onAuthenticated={setSession} />;
}
