import { FormEvent, useEffect, useState } from "react";
import { AuthSession, loginWithBackend } from "../services/auth";
import { AlertIcon, CheckIcon, EyeIcon, LockIcon, SpinnerIcon, UserIcon } from "../shared/icons";

type LoginStatus = "idle" | "error" | "authenticating" | "success";

type LoginPageProps = {
  onAuthenticated: (session: AuthSession) => void;
};

export function LoginPage({ onAuthenticated }: LoginPageProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<LoginStatus>("idle");
  const [errorMessage, setErrorMessage] = useState("Credenciais inválidas. Verifique o email e a palavra-passe.");
  const [authenticatedSession, setAuthenticatedSession] = useState<AuthSession | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const isAuthenticating = status === "authenticating" || status === "success";

  useEffect(() => {
    if (status !== "success") {
      return undefined;
    }

    const redirectTimer = window.setTimeout(() => {
      if (authenticatedSession) {
        onAuthenticated(authenticatedSession);
      }
    }, 900);

    return () => window.clearTimeout(redirectTimer);
  }, [authenticatedSession, onAuthenticated, status]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isAuthenticating) {
      return;
    }

    setStatus("authenticating");
    setErrorMessage("Credenciais inválidas. Verifique o email e a palavra-passe.");

    try {
      const session = await loginWithBackend(email, password);
      setAuthenticatedSession(session);
      setStatus("success");
    } catch (error) {
      setAuthenticatedSession(null);
      setErrorMessage(error instanceof Error ? error.message : "Não foi possível iniciar sessão.");
      setStatus("error");
    }
  }

  return (
    <main className="login-page" data-node-id="11:5">
      <section className="brand-panel" aria-label="Associação Agrícola">
        <div className="brand-orb brand-orb-large" />
        <div className="brand-orb brand-orb-bottom" />
        <div className="brand-orb brand-orb-medium" />
        <div className="brand-orb brand-orb-small-right" />
        <div className="brand-orb brand-orb-small-left" />

        <div className="brand-lines" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>

        <div className="brand-copy">
          <h1>Associação Agrícola</h1>
          <p>Sistema de Gestão Integrado</p>
        </div>

        <p className="brand-footer">© 2025 Associação Agrícola</p>
      </section>

      <section className="login-panel" aria-labelledby="login-title">
        <form className={`login-card login-card-${status}`} onSubmit={handleSubmit}>
          <header className="login-header">
            <h2 id="login-title">Bem-vindo</h2>
            <p>Inicie sessão para continuar</p>
          </header>

          <label className="field">
            <span>Email</span>
            <span className="input-shell">
              <UserIcon aria-hidden="true" />
              <input
                autoComplete="email"
                disabled={isAuthenticating}
                inputMode="email"
                name="email"
                onChange={(event) => {
                  setEmail(event.target.value);
                  if (status === "error") {
                    setStatus("idle");
                  }
                }}
                placeholder="exemplo@associacao.pt"
                type="email"
                value={email}
              />
            </span>
          </label>

          <label className="field">
            <span>Palavra-passe</span>
            <span className="input-shell">
              <LockIcon aria-hidden="true" />
              <input
                autoComplete="current-password"
                disabled={isAuthenticating}
                name="password"
                onChange={(event) => {
                  setPassword(event.target.value);
                  if (status === "error") {
                    setStatus("idle");
                  }
                }}
                placeholder="••••••••"
                type={showPassword ? "text" : "password"}
                value={password}
              />
              <button
                className="icon-button"
                type="button"
                aria-label={showPassword ? "Ocultar palavra-passe" : "Mostrar palavra-passe"}
                disabled={isAuthenticating}
                onClick={() => setShowPassword((current) => !current)}
              >
                <EyeIcon aria-hidden="true" />
              </button>
            </span>
          </label>

          {status === "error" && (
            <div className="login-alert login-alert-error" role="alert">
              <AlertIcon aria-hidden="true" />
              <span>{errorMessage}</span>
            </div>
          )}

          {isAuthenticating ? (
            <button className="submit-button submit-button-loading" type="button" disabled>
              <SpinnerIcon aria-hidden="true" />
              A autenticar...
            </button>
          ) : (
            <button className="submit-button" type="submit">
              {status === "error" ? "Tentar novamente" : "Entrar"}
            </button>
          )}

          {status === "success" && (
            <div className="login-alert login-alert-success" role="status">
              <CheckIcon aria-hidden="true" />
              <span>Autenticação bem-sucedida. A redirecionar...</span>
            </div>
          )}
        </form>
      </section>
    </main>
  );
}
