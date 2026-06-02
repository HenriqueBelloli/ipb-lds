import { FormEvent, useEffect, useState } from "react";
import { EyeIcon, PencilIcon } from "../shared/icons";
import {
  createDelegation,
  Delegation,
  DelegationInput,
  listDelegations,
  updateDelegation,
} from "../services/management";
import { formatDateTime, shortenId } from "./AuditLogsPage";

type ModalMode = "view" | "edit" | "create";

type DelegationFormState = DelegationInput & {
  id?: string;
};

const emptyForm: DelegationFormState = {
  codigo: "",
  nome: "",
  localizacao: "",
  responsavelId: null,
  ativo: true,
};

export function AdminDelegationsPage() {
  const [delegations, setDelegations] = useState<Delegation[]>([]);
  const [form, setForm] = useState<DelegationFormState>(emptyForm);
  const [modalMode, setModalMode] = useState<ModalMode | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    loadDelegations();
  }, []);

  async function loadDelegations() {
    setIsLoading(true);
    setError(null);

    try {
      setDelegations(await listDelegations());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Não foi possível carregar delegações.");
    } finally {
      setIsLoading(false);
    }
  }

  function openCreateForm() {
    setForm(emptyForm);
    setFeedback(null);
    setModalMode("create");
  }

  function openDelegationModal(delegation: Delegation, mode: "view" | "edit") {
    setForm({
      id: delegation.id,
      codigo: delegation.codigo,
      nome: delegation.nome,
      localizacao: delegation.localizacao,
      responsavelId: delegation.responsavelId,
      ativo: delegation.ativo,
    });
    setFeedback(null);
    setModalMode(mode);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setFeedback(null);

    try {
      const input = {
        codigo: form.codigo,
        nome: form.nome,
        localizacao: form.localizacao,
        responsavelId: form.responsavelId?.trim() || null,
        ativo: form.ativo,
      };

      if (form.id) {
        await updateDelegation(form.id, input);
        setFeedback("Delegação actualizada.");
      } else {
        await createDelegation(input);
        setFeedback("Delegação criada.");
      }

      setModalMode(null);
      await loadDelegations();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Não foi possível guardar a delegação.");
    }
  }

  const isReadOnly = modalMode === "view";

  return (
    <section className="data-page admin-page">
      <div className="content-actions-row">
        <h2>Gestão de Delegações</h2>
        <button className="primary-action" type="button" onClick={openCreateForm}>
          <span aria-hidden="true">+</span>
          Nova Delegação
        </button>
      </div>

      <div className="summary-grid" aria-label="Resumo de delegações">
        <article className="metric-card"><strong>{delegations.length}</strong><span>Delegações activas</span></article>
        <article className="metric-card metric-success"><strong>{delegations.filter((item) => item.responsavelId).length}</strong><span>Com responsável</span></article>
        <article className="metric-card metric-warning"><strong>{delegations.filter((item) => !item.responsavelId).length}</strong><span>Sem responsável</span></article>
        <article className="metric-card metric-default"><strong>{new Set(delegations.map((item) => item.localizacao)).size}</strong><span>Localizações</span></article>
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
                <h3>{modalMode === "create" ? "Nova Delegação" : modalMode === "edit" ? "Editar Delegação" : "Detalhe da Delegação"}</h3>
                <p>{isReadOnly ? "Consulta dos dados da delegação" : "Preencha os dados obrigatórios"}</p>
              </div>
              <button className="icon-button" type="button" aria-label="Fechar" onClick={() => setModalMode(null)}>×</button>
            </header>
            <div className="detail-divider" />
            <div className="form-grid">
              <label className="field-block">
                <span>Código</span>
                <input disabled={isReadOnly} required value={form.codigo} onChange={(event) => setForm((current) => ({ ...current, codigo: event.target.value }))} />
              </label>
              <label className="field-block">
                <span>Nome</span>
                <input disabled={isReadOnly} required value={form.nome} onChange={(event) => setForm((current) => ({ ...current, nome: event.target.value }))} />
              </label>
              <label className="field-block field-wide">
                <span>Localização</span>
                <input disabled={isReadOnly} required value={form.localizacao} onChange={(event) => setForm((current) => ({ ...current, localizacao: event.target.value }))} />
              </label>
              <label className="field-block field-wide">
                <span>ID do responsável</span>
                <input disabled={isReadOnly} value={form.responsavelId ?? ""} onChange={(event) => setForm((current) => ({ ...current, responsavelId: event.target.value }))} />
              </label>
              {form.id && (
                <label className="checkbox-field">
                  <input disabled={isReadOnly} type="checkbox" checked={form.ativo} onChange={(event) => setForm((current) => ({ ...current, ativo: event.target.checked }))} />
                  <span>Delegação activa</span>
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
          <table className="data-table admin-delegations-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Nome</th>
                <th>Localização</th>
                <th>Responsável</th>
                <th>Criada em</th>
                <th className="actions-cell">Acções</th>
              </tr>
            </thead>
            <tbody>
              {delegations.map((delegation) => (
                <tr key={delegation.id}>
                  <td>{delegation.codigo}</td>
                  <td>{delegation.nome}</td>
                  <td>{delegation.localizacao}</td>
                  <td>{shortenId(delegation.responsavelId)}</td>
                  <td>{formatDateTime(delegation.createdAt)}</td>
                  <td className="actions-cell">
                    <button type="button" aria-label={`Ver ${delegation.nome}`} title="Ver detalhes" onClick={() => openDelegationModal(delegation, "view")}><EyeIcon aria-hidden="true" /></button>
                    <button type="button" aria-label={`Editar ${delegation.nome}`} title="Editar" onClick={() => openDelegationModal(delegation, "edit")}><PencilIcon aria-hidden="true" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <footer className="data-pagination">
          <span>{isLoading ? "A carregar delegações..." : `Mostrando ${delegations.length} delegações`}</span>
        </footer>
      </div>
    </section>
  );
}
