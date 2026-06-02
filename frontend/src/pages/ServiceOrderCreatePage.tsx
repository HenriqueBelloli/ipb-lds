import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { Client, listClients } from "../services/clients";
import { Delegation, listDelegations } from "../services/management";
import {
  createServiceOrder,
  DelegationService,
  listDelegationServices,
  ServiceOrder,
  ServiceOrderCreateInput,
} from "../services/serviceOrders";
import { LockIcon, SearchIcon } from "../shared/icons";

type PriceType = ServiceOrderCreateInput["priceType"];

type ServiceOrderCreatePageProps = {
  onCancel: () => void;
  onCreated: (order: ServiceOrder) => void;
};

type SelectedService = {
  bonified: boolean;
};

export function ServiceOrderCreatePage({ onCancel, onCreated }: ServiceOrderCreatePageProps) {
  const [clients, setClients] = useState<Client[]>([]);
  const [delegations, setDelegations] = useState<Delegation[]>([]);
  const [delegationServices, setDelegationServices] = useState<DelegationService[]>([]);
  const [clientQuery, setClientQuery] = useState("");
  const [serviceQuery, setServiceQuery] = useState("");
  const [selectedClientId, setSelectedClientId] = useState("");
  const [selectedDelegationId, setSelectedDelegationId] = useState("");
  const [priceType, setPriceType] = useState<PriceType>("NAO_ASSOCIADO");
  const [selectedServices, setSelectedServices] = useState<Record<string, SelectedService>>({});
  const [expectedDate, setExpectedDate] = useState("");
  const [notes, setNotes] = useState("");
  const [isLoadingInitialData, setIsLoadingInitialData] = useState(true);
  const [isLoadingServices, setIsLoadingServices] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedClient = clients.find((client) => client.id === selectedClientId);
  const selectedServiceRows = delegationServices.filter((service) => selectedServices[service.id]);
  const totalAmount = selectedServiceRows.reduce(
    (total, service) => total + (selectedServices[service.id]?.bonified ? 0 : service.appliedPrice),
    0,
  );
  const entryPercent = selectedServiceRows.reduce((highest, service) => Math.max(highest, service.entryPercent), 0);

  const clientOptions = useMemo(
    () =>
      clients.map((client) => ({
        label: getClientOptionLabel(client),
        value: client.id,
      })),
    [clients],
  );

  const serviceOptions = useMemo(
    () =>
      delegationServices
        .filter((service) => !selectedServices[service.id])
        .map((service) => ({
          label: getServiceOptionLabel(service),
          value: service.id,
        })),
    [delegationServices, selectedServices],
  );

  useEffect(() => {
    let isMounted = true;

    async function loadInitialData() {
      try {
        setIsLoadingInitialData(true);
        setError(null);
        const [nextDelegations, nextClients] = await Promise.all([
          listDelegations(),
          listClients({ status: "active" }),
        ]);

        if (isMounted) {
          setDelegations(nextDelegations);
          setClients(nextClients);
        }
      } catch (loadError) {
        if (isMounted) {
          setError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar os dados para criar a OS.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingInitialData(false);
        }
      }
    }

    loadInitialData();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedClient) {
      return;
    }

    setClientQuery(getClientOptionLabel(selectedClient));
    setPriceType(selectedClient.associated ? "ASSOCIADO" : "NAO_ASSOCIADO");
  }, [selectedClient]);

  useEffect(() => {
    let isMounted = true;

    async function loadServices() {
      if (!selectedDelegationId) {
        setDelegationServices([]);
        setSelectedServices({});
        return;
      }

      try {
        setIsLoadingServices(true);
        setError(null);
        const services = await listDelegationServices(selectedDelegationId, priceType);

        if (isMounted) {
          setDelegationServices(services);
          setSelectedServices({});
          setServiceQuery("");
        }
      } catch (loadError) {
        if (isMounted) {
          setDelegationServices([]);
          setSelectedServices({});
          setError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar os servicos da delegacao.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingServices(false);
        }
      }
    }

    loadServices();

    return () => {
      isMounted = false;
    };
  }, [priceType, selectedDelegationId]);

  function handleClientInputChange(value: string) {
    setClientQuery(value);
    const exactOption = clientOptions.find((option) => option.label === value);
    setSelectedClientId(exactOption?.value ?? "");
  }

  function handleServiceInputChange(value: string) {
    setServiceQuery(value);
    const exactOption = serviceOptions.find((option) => option.label === value);

    if (exactOption) {
      addService(exactOption.value);
    }
  }

  function addService(serviceId: string) {
    setSelectedServices((current) => ({
      ...current,
      [serviceId]: { bonified: false },
    }));
    setServiceQuery("");
  }

  function removeService(serviceId: string) {
    setSelectedServices((current) => {
      const next = { ...current };
      delete next[serviceId];
      return next;
    });
  }

  function toggleBonified(serviceId: string, checked: boolean) {
    setSelectedServices((current) => ({
      ...current,
      [serviceId]: {
        bonified: checked,
      },
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!selectedDelegationId) {
      setError("Selecione a delegacao de execucao.");
      return;
    }

    if (!selectedClientId) {
      setError("Selecione um cliente da lista.");
      return;
    }

    if (!selectedServiceRows.length) {
      setError("Selecione pelo menos um servico.");
      return;
    }

    if (!expectedDate) {
      setError("Indique a data prevista.");
      return;
    }

    try {
      setIsSaving(true);
      const createdOrder = await createServiceOrder({
        clientId: selectedClientId,
        executionDelegationId: selectedDelegationId,
        priceType,
        items: selectedServiceRows.map((service) => ({
          serviceId: service.serviceId,
          serviceDelegationId: service.id,
          appliedPrice: service.appliedPrice,
          bonified: selectedServices[service.id]?.bonified ?? false,
        })),
      });
      onCreated(createdOrder);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Nao foi possivel criar a ordem de servico.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="service-order-create-page">
      <nav className="detail-breadcrumb os-create-breadcrumb" aria-label="Navegacao">
        <button type="button" onClick={onCancel}>
          Ordens de Servico
        </button>
        <span>&gt;</span>
        <strong>Nova OS</strong>
      </nav>

      <form className="os-create-card" onSubmit={handleSubmit}>
        {error ? <div className="login-alert login-alert-error">{error}</div> : null}
        {isLoadingInitialData ? <div className="orders-message">A carregar dados da OS...</div> : null}

        <FormSection title="Informacoes Gerais">
          <div className="os-create-two-columns">
            <label className="os-field">
              <span>
                Delegacao de Execucao <strong>*</strong>
              </span>
              <select
                value={selectedDelegationId}
                onChange={(event) => setSelectedDelegationId(event.target.value)}
                disabled={isLoadingInitialData}
              >
                <option value="">Seleccione a delegacao</option>
                {delegations.map((delegation) => (
                  <option key={delegation.id} value={delegation.id}>
                    {delegation.nome}
                  </option>
                ))}
              </select>
              <small>A delegacao define os servicos disponiveis</small>
            </label>

            <label className="os-field">
              <span>
                Cliente <strong>*</strong>
              </span>
              <div className="os-search-input">
                <SearchIcon aria-hidden="true" />
                <input
                  list="service-order-client-options"
                  value={clientQuery}
                  onChange={(event) => handleClientInputChange(event.target.value)}
                  placeholder="Pesquisar por nome ou NIF..."
                  disabled={isLoadingInitialData}
                />
                <datalist id="service-order-client-options">
                  {clientOptions.map((client) => (
                    <option key={client.value} value={client.label} />
                  ))}
                </datalist>
              </div>
            </label>
          </div>
        </FormSection>

        <FormSection title="Servicos">
          <label className="os-field">
            <div className={`os-search-input${!selectedDelegationId ? " os-search-input-disabled" : ""}`}>
              <SearchIcon aria-hidden="true" />
              <input
                list="service-order-service-options"
                value={serviceQuery}
                onChange={(event) => handleServiceInputChange(event.target.value)}
                placeholder="Pesquisar servico..."
                disabled={!selectedDelegationId || isLoadingServices}
              />
              {!selectedDelegationId ? <LockIcon aria-hidden="true" /> : null}
              <datalist id="service-order-service-options">
                {serviceOptions.map((service) => (
                  <option key={service.value} value={service.label} />
                ))}
              </datalist>
            </div>
            <small>{selectedDelegationId ? "Seleccione um servico da lista" : "Disponivel apos seleccionar a delegacao"}</small>
          </label>

          <div className="os-services-available-box">
            {selectedDelegationId ? (
              isLoadingServices ? (
                <span>A carregar servicos disponiveis...</span>
              ) : delegationServices.length ? (
                <span>{delegationServices.length} servico(s) disponivel(is) para pesquisa</span>
              ) : (
                <span>Nenhum servico disponivel nesta delegacao</span>
              )
            ) : (
              <>
                <span className="os-empty-icon">=</span>
                <span>Seleccione uma delegacao para ver os servicos disponiveis</span>
              </>
            )}
          </div>

          {selectedServiceRows.length ? (
            <div className="os-selected-services-box">
              <div className="os-selected-services-header">
                <span>Servico</span>
                <span>Entrada</span>
                <span>Valor</span>
                <span>Bonificar</span>
                <span />
              </div>
              {selectedServiceRows.map((service) => {
                const isBonified = selectedServices[service.id]?.bonified ?? false;

                return (
                  <div className="os-selected-service-row" key={service.id}>
                    <div>
                      <strong>{service.name}</strong>
                      <small>{service.description ?? "Sem descricao"}</small>
                    </div>
                    <span>{formatPercent(service.entryPercent)}</span>
                    <span>{formatCurrency(isBonified ? 0 : service.appliedPrice)}</span>
                    <label>
                      <input
                        type="checkbox"
                        checked={isBonified}
                        disabled={!service.bonifiable}
                        onChange={(event) => toggleBonified(service.id, event.target.checked)}
                      />
                      Sim
                    </label>
                    <button type="button" onClick={() => removeService(service.id)}>
                      Remover
                    </button>
                  </div>
                );
              })}
              <div className="os-selected-services-total">
                <span>Total</span>
                <strong>{formatCurrency(totalAmount)}</strong>
              </div>
            </div>
          ) : (
            <div className="os-selected-empty-box">
              <strong>Nenhum servico seleccionado</strong>
              <span>O total sera calculado apos seleccionar os servicos</span>
            </div>
          )}
        </FormSection>

        <FormSection title="Detalhes">
          <div className="os-create-two-columns">
            <label className="os-field">
              <span>
                Data Prevista <strong>*</strong>
              </span>
              <input type="date" value={expectedDate} onChange={(event) => setExpectedDate(event.target.value)} />
            </label>

            <label className="os-field">
              <span>Percentagem de Entrada</span>
              <div className="os-locked-input">
                <input value={selectedServiceRows.length ? formatPercent(entryPercent) : "-"} readOnly />
                <LockIcon aria-hidden="true" />
              </div>
              <small>Definida na configuracao do servico</small>
            </label>
          </div>

          <label className="os-field os-notes-field">
            <span>Observacoes</span>
            <textarea
              maxLength={500}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Informacoes adicionais..."
            />
            <small>{notes.length}/500</small>
          </label>
        </FormSection>

        <div className="os-create-actions">
          <button className="clear-button" type="button" onClick={onCancel} disabled={isSaving}>
            Cancelar
          </button>
          <button
            className="primary-action"
            type="submit"
            disabled={isSaving || isLoadingInitialData || isLoadingServices || !selectedDelegationId || !selectedClientId || !selectedServiceRows.length || !expectedDate}
          >
            {isSaving ? "A criar..." : "Criar OS"}
          </button>
        </div>
      </form>
    </section>
  );
}

function FormSection({ children, title }: { children: ReactNode; title: string }) {
  return (
    <section className="os-form-section">
      <h3>{title}</h3>
      <div className="os-section-divider" />
      {children}
    </section>
  );
}

function getClientOptionLabel(client: Client) {
  return `${client.name} - NIF ${client.nif}`;
}

function getServiceOptionLabel(service: DelegationService) {
  return `${service.name} - ${formatCurrency(service.appliedPrice)}`;
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-PT", {
    style: "currency",
    currency: "EUR",
  }).format(Number.isFinite(value) ? value : 0);
}

function formatPercent(value: number) {
  return `${new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 2 }).format(Number.isFinite(value) ? value : 0)}%`;
}
