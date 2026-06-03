import { FormEvent, useState } from "react";
import { Client, ClientUpdateInput, updateClient } from "../services/clients";

type ClientEditPageProps = {
  client: Client;
  onCancel: () => void;
  onSaved: (client: Client) => void;
};

export function ClientEditPage({ client, onCancel, onSaved }: ClientEditPageProps) {
  const [form, setForm] = useState<ClientUpdateInput>({
    nif: client.nif,
    nome: client.name,
    telefone: emptyDash(client.phone),
    email: emptyDash(client.email),
    morada: emptyDash(client.address),
    flagAssociado: client.associated,
    ativo: client.status === "Activo",
  });
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!form.nome.trim()) {
      setError("Indique o nome do cliente.");
      return;
    }

    if (!form.nif.trim()) {
      setError("Indique o NIF do cliente.");
      return;
    }

    try {
      setIsSaving(true);
      const savedClient = await updateClient(client.id, {
        ...form,
        nome: form.nome.trim(),
        nif: form.nif.trim(),
        telefone: form.telefone.trim(),
        email: form.email.trim(),
        morada: form.morada.trim(),
      });
      onSaved(savedClient);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Nao foi possivel guardar o cliente.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="client-detail-page">
      <nav className="detail-breadcrumb" aria-label="Navegacao">
        <button type="button" onClick={onCancel}>Clientes</button>
        <span>&gt;</span>
        <button type="button" onClick={onCancel}>{client.name}</button>
        <span>&gt;</span>
        <strong>Editar</strong>
      </nav>

      <form className="detail-card client-form-card" onSubmit={handleSubmit}>
        <header className="detail-card-header">
          <div>
            <h3>Editar Cliente</h3>
          </div>
          <span className={`status-pill ${form.ativo ? "status-done" : "status-muted"}`}>{form.ativo ? "Activo" : "Inactivo"}</span>
        </header>

        <div className="detail-divider" />

        {error ? <div className="login-alert login-alert-error">{error}</div> : null}

        <div className="form-grid">
          <label className="field-block field-wide">
            <span>Nome Completo *</span>
            <input
              value={form.nome}
              onChange={(event) => setForm((current) => ({ ...current, nome: event.target.value }))}
            />
          </label>

          <label className="field-block">
            <span>NIF *</span>
            <input
              value={form.nif}
              onChange={(event) => setForm((current) => ({ ...current, nif: event.target.value }))}
            />
          </label>

          <label className="field-block">
            <span>Telefone</span>
            <input
              value={form.telefone}
              onChange={(event) => setForm((current) => ({ ...current, telefone: event.target.value }))}
            />
          </label>

          <label className="field-block field-wide">
            <span>Email</span>
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
            />
          </label>

          <label className="field-block field-wide">
            <span>Morada</span>
            <input
              value={form.morada}
              onChange={(event) => setForm((current) => ({ ...current, morada: event.target.value }))}
            />
          </label>

          <label className="checkbox-field">
            <input
              type="checkbox"
              checked={form.flagAssociado}
              onChange={(event) => setForm((current) => ({ ...current, flagAssociado: event.target.checked }))}
            />
            Associado
          </label>

          <label className="checkbox-field">
            <input
              type="checkbox"
              checked={form.ativo}
              onChange={(event) => setForm((current) => ({ ...current, ativo: event.target.checked }))}
            />
            Cliente activo
          </label>
        </div>

        <div className="profile-dialog-actions">
          <button className="clear-button" type="button" onClick={onCancel} disabled={isSaving}>Cancelar</button>
          <button className="primary-action" type="submit" disabled={isSaving}>
            {isSaving ? "A guardar..." : "Guardar"}
          </button>
        </div>
      </form>
    </section>
  );
}

function emptyDash(value: string) {
  return value === "-" ? "" : value;
}
