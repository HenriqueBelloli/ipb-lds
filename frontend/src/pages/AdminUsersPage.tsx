import { FormEvent, useEffect, useMemo, useState } from "react";
import { EyeIcon, PencilIcon } from "../shared/icons";
import {
  createUser,
  Delegation,
  listDelegations,
  listUsers,
  ManagedUser,
  updateUser,
  UserProfile,
} from "../services/management";
import { formatDateTime, shortenId } from "./AuditLogsPage";

type ModalMode = "view" | "edit" | "create";

type UserFormState = {
  id?: string;
  nome: string;
  email: string;
  password: string;
  perfil: UserProfile;
  delegacaoId: string;
  ativo: boolean;
};

const emptyForm: UserFormState = {
  nome: "",
  email: "",
  password: "",
  perfil: "OPERADOR",
  delegacaoId: "",
  ativo: true,
};

const profileLabels: Record<UserProfile, string> = {
  OPERADOR: "Operador",
  GESTOR: "Gestor",
  FINANCEIRO: "Financeiro",
  DIRECAO: "Direção",
  ADMINISTRADOR: "Administrador",
};

export function AdminUsersPage() {
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [delegations, setDelegations] = useState<Delegation[]>([]);
  const [form, setForm] = useState<UserFormState>(emptyForm);
  const [modalMode, setModalMode] = useState<ModalMode | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const delegationById = useMemo(() => {
    return new Map(delegations.map((delegation) => [delegation.id, delegation]));
  }, [delegations]);

  async function loadData() {
    setIsLoading(true);
    setError(null);

    try {
      const [usersResult, delegationsResult] = await Promise.all([listUsers(), listDelegations()]);
      setUsers(usersResult);
      setDelegations(delegationsResult);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Não foi possível carregar utilizadores.");
    } finally {
      setIsLoading(false);
    }
  }

  function openCreateForm() {
    setForm({ ...emptyForm, delegacaoId: delegations[0]?.id ?? "" });
    setFeedback(null);
    setModalMode("create");
  }

  function openUserModal(user: ManagedUser, mode: "view" | "edit") {
    setForm({
      id: user.id,
      nome: user.nome,
      email: user.email,
      password: "",
      perfil: user.perfil,
      delegacaoId: user.delegacaoId ?? "",
      ativo: user.ativo,
    });
    setFeedback(null);
    setModalMode(mode);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setFeedback(null);

    try {
      if (form.id) {
        await updateUser(form.id, {
          nome: form.nome,
          email: form.email,
          perfil: form.perfil,
          delegacaoId: form.delegacaoId,
          ativo: form.ativo,
        });
        setFeedback("Utilizador actualizado.");
      } else {
        await createUser({
          nome: form.nome,
          email: form.email,
          password: form.password,
          perfil: form.perfil,
          delegacaoId: form.delegacaoId,
        });
        setFeedback("Utilizador criado.");
      }

      setModalMode(null);
      await loadData();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Não foi possível guardar o utilizador.");
    }
  }

  const isReadOnly = modalMode === "view";

  return (
    <section className="data-page admin-page">
      <div className="content-actions-row">
        <h2>Gestão de Utilizadores</h2>
        <button className="primary-action" type="button" onClick={openCreateForm}>
          <span aria-hidden="true">+</span>
          Novo Utilizador
        </button>
      </div>

      <div className="summary-grid" aria-label="Resumo de utilizadores">
        <article className="metric-card"><strong>{users.length}</strong><span>Utilizadores activos</span></article>
        <article className="metric-card metric-success"><strong>{delegations.length}</strong><span>Delegações disponíveis</span></article>
        <article className="metric-card metric-warning"><strong>{users.filter((user) => user.perfil === "ADMINISTRADOR").length}</strong><span>Administradores</span></article>
        <article className="metric-card metric-default"><strong>{users.filter((user) => user.perfil === "OPERADOR").length}</strong><span>Operadores</span></article>
      </div>

      {(error || feedback) && (
        <div className={`admin-message ${error ? "admin-message-error" : "admin-message-success"}`}>
          {error ?? feedback}
        </div>
      )}

      {modalMode && (
        <div className="modal-overlay" role="presentation">
          <form className="admin-modal detail-card" onSubmit={handleSubmit}>
            <header className="modal-header">
              <div>
                <h3>{modalMode === "create" ? "Novo Utilizador" : modalMode === "edit" ? "Editar Utilizador" : "Detalhe do Utilizador"}</h3>
                <p>{isReadOnly ? "Consulta dos dados do utilizador" : "Preencha os dados obrigatórios"}</p>
              </div>
              <button className="icon-button" type="button" aria-label="Fechar" onClick={() => setModalMode(null)}>×</button>
            </header>
            <div className="detail-divider" />
            <div className="form-grid">
              <label className="field-block field-wide">
                <span>Nome</span>
                <input disabled={isReadOnly} required value={form.nome} onChange={(event) => setForm((current) => ({ ...current, nome: event.target.value }))} />
              </label>
              <label className="field-block">
                <span>Email</span>
                <input disabled={isReadOnly} required type="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} />
              </label>
              {modalMode === "create" && (
                <label className="field-block">
                  <span>Password</span>
                  <input required type="password" value={form.password} onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} />
                </label>
              )}
              <label className="field-block">
                <span>Perfil</span>
                <select disabled={isReadOnly} value={form.perfil} onChange={(event) => setForm((current) => ({ ...current, perfil: event.target.value as UserProfile }))}>
                  {Object.entries(profileLabels).map(([value, label]) => <option value={value} key={value}>{label}</option>)}
                </select>
              </label>
              <label className="field-block">
                <span>Delegação</span>
                <select disabled={isReadOnly} required value={form.delegacaoId} onChange={(event) => setForm((current) => ({ ...current, delegacaoId: event.target.value }))}>
                  <option value="">Seleccione</option>
                  {delegations.map((delegation) => <option value={delegation.id} key={delegation.id}>{delegation.nome}</option>)}
                </select>
              </label>
              {form.id && (
                <label className="checkbox-field">
                  <input disabled={isReadOnly} type="checkbox" checked={form.ativo} onChange={(event) => setForm((current) => ({ ...current, ativo: event.target.checked }))} />
                  <span>Utilizador activo</span>
                </label>
              )}
            </div>
            <footer className="admin-form-actions">
              {isReadOnly && <button className="detail-button detail-button-neutral" type="button" onClick={() => setModalMode("edit")}>Editar</button>}
              <button className="detail-button detail-button-neutral" type="button" onClick={() => setModalMode(null)}>{isReadOnly ? "Fechar" : "Cancelar"}</button>
              {!isReadOnly && <button className="detail-button detail-button-success" type="submit">Guardar</button>}
            </footer>
          </form>
        </div>
      )}

      <div className="data-table-card">
        <div className="data-table-wrap">
          <table className="data-table admin-users-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Email</th>
                <th>Perfil</th>
                <th>Delegação</th>
                <th>Criado em</th>
                <th className="actions-cell">Acções</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.nome}</td>
                  <td>{user.email}</td>
                  <td><span className="status-pill status-running">{profileLabels[user.perfil]}</span></td>
                  <td>{user.delegacaoId ? delegationById.get(user.delegacaoId)?.nome ?? shortenId(user.delegacaoId) : "-"}</td>
                  <td>{formatDateTime(user.createdAt)}</td>
                  <td className="actions-cell">
                    <button type="button" aria-label={`Ver ${user.nome}`} title="Ver detalhes" onClick={() => openUserModal(user, "view")}><EyeIcon aria-hidden="true" /></button>
                    <button type="button" aria-label={`Editar ${user.nome}`} title="Editar" onClick={() => openUserModal(user, "edit")}><PencilIcon aria-hidden="true" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <footer className="data-pagination">
          <span>{isLoading ? "A carregar utilizadores..." : `Mostrando ${users.length} utilizadores`}</span>
        </footer>
      </div>
    </section>
  );
}
