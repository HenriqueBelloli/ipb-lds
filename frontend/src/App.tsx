import { useState } from "react";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { AuthSession, getStoredSession, logoutFromBackend, updateStoredUser } from "./services/auth";

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

  function handleUserUpdated(user: AppUser) {
    const updatedSession = updateStoredUser(user);

    if (updatedSession) {
      setSession(updatedSession);
    }
  }

  if (session) {
    return <DashboardPage user={session.user} onLogout={handleLogout} onUserUpdated={handleUserUpdated} />;
  }

  return <LoginPage onAuthenticated={setSession} />;
}
