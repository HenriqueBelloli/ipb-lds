import { FormEvent, useEffect, useRef, useState } from "react";
import { AppUser } from "../App";
import { AuditLog } from "../services/audit";
import { Client } from "../services/clients";
import { changeOwnPassword, updateOwnProfile } from "../services/management";
import { getNotification, listNotifications, Notification } from "../services/notifications";
import { ServiceOrder } from "../services/serviceOrders";
import { AdminDelegationsPage } from "./AdminDelegationsPage";
import { AdminUsersPage } from "./AdminUsersPage";
import { AuditLogDetailPage } from "./AuditLogDetailPage";
import { AuditLogsPage } from "./AuditLogsPage";
import { ClientsPage } from "./ClientsPage";
import { ClientDetailPage } from "./ClientDetailPage";
import { ClientEditPage } from "./ClientEditPage";
import { FinanceReceivablesPage } from "./FinanceReceivablesPage";
import { ServiceOrderCreatePage } from "./ServiceOrderCreatePage";
import { ServiceOrdersPage } from "./ServiceOrdersPage";
import { ServiceOrderDetailPage } from "./ServiceOrderDetailPage";
import {
  BellIcon,
  ClipboardIcon,
  FileIcon,
  LogoutIcon,
  MoneyIcon,
  UsersIcon,
} from "../shared/icons";

type DashboardPageProps = {
  user: AppUser;
  onLogout: () => void;
  onUserUpdated: (user: AppUser) => void;
};

type AppSection = "orders" | "finance" | "clients" | "audit" | "users" | "delegations";

const menuItems = [
  { id: "orders", label: "Ordens de Serviço", icon: ClipboardIcon },
  { id: "finance", label: "Financeiro", icon: MoneyIcon },
  { id: "clients", label: "Clientes", icon: UsersIcon },
  { id: "audit", label: "Auditoria", icon: FileIcon },
  { id: "users", label: "Utilizadores", icon: UsersIcon, adminOnly: true },
  { id: "delegations", label: "Delegações", icon: FileIcon, adminOnly: true },
] satisfies Array<{
  id: AppSection;
  label: string;
  icon: typeof ClipboardIcon;
  adminOnly?: boolean;
}>;

const sectionTitles: Record<AppSection, string> = {
  orders: "Ordens de Serviço",
  finance: "Contas a Receber",
  clients: "Clientes",
  audit: "Auditoria",
  users: "Gestão de Utilizadores",
  delegations: "Gestão de Delegações",
};

const emptySectionLabels: Record<AppSection, string> = {
  orders: "Ordens de Serviço",
  finance: "Área financeira vazia",
  clients: "Área de clientes vazia",
  audit: "Área de auditoria vazia",
  users: "Área de utilizadores vazia",
  delegations: "Área de delegações vazia",
};

const emptySectionTitles: Record<AppSection, string> = {
  orders: "",
  finance: "Financeiro",
  clients: "Clientes",
  audit: "Auditoria",
  users: "Utilizadores",
  delegations: "Delegações",
};

const emptySectionCopy: Record<AppSection, string> = {
  orders: "",
  finance: "Este módulo será implementado a seguir.",
  clients: "Este módulo será implementado a seguir.",
  audit: "Este módulo será implementado a seguir.",
  users: "Este módulo será implementado a seguir.",
  delegations: "Este módulo será implementado a seguir.",
};

const contentFor = {
  orders: null,
  finance: null,
  clients: null,
  audit: null,
  users: null,
  delegations: null,
};

function EmptyWorkspace({ section }: { section: AppSection }) {
  return (
    <div className="empty-workspace empty-module" aria-label={emptySectionLabels[section]}>
      <div>
        <h2>{emptySectionTitles[section]}</h2>
        <p>{emptySectionCopy[section]}</p>
      </div>
    </div>
  );
}

function getContent(section: AppSection) {
  return contentFor[section] ?? <EmptyWorkspace section={section} />;
}

export function DashboardPage({ user, onLogout, onUserUpdated }: DashboardPageProps) {
  const [activeSection, setActiveSection] = useState<AppSection>("orders");
  const [selectedOrder, setSelectedOrder] = useState<ServiceOrder | null>(null);
  const [isCreatingOrder, setIsCreatingOrder] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [selectedAuditLog, setSelectedAuditLog] = useState<AuditLog | null>(null);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(false);
  const [isLoadingNotificationDetail, setIsLoadingNotificationDetail] = useState(false);
  const [notificationError, setNotificationError] = useState<string | null>(null);
  const [isProfileDialogOpen, setIsProfileDialogOpen] = useState(false);
  const [profileForm, setProfileForm] = useState({
    name: user.name,
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const notificationPanelRef = useRef<HTMLDivElement | null>(null);
  const unreadNotificationsCount = notifications.filter((notification) => !notification.lida).length;

  const pageTitle = selectedOrder
    ? "Detalhe da Ordem de Serviço"
    : isCreatingOrder
      ? "Criar Ordem de ServiÃ§o"
      : editingClient
        ? "Editar Cliente"
        : selectedClient
          ? "Detalhe do Cliente"
          : selectedAuditLog
            ? "Detalhe do Log"
            : sectionTitles[activeSection];

  function handleSectionChange(section: AppSection) {
    setActiveSection(section);
    setSelectedOrder(null);
    setIsCreatingOrder(false);
    setSelectedClient(null);
    setEditingClient(null);
    setSelectedAuditLog(null);
  }

  function handleViewOrder(order: ServiceOrder) {
    setActiveSection("orders");
    setSelectedOrder(order);
    setIsCreatingOrder(false);
    setSelectedClient(null);
    setEditingClient(null);
    setSelectedAuditLog(null);
  }

  function handleViewClient(client: Client) {
    setActiveSection("clients");
    setSelectedClient(client);
    setEditingClient(null);
    setSelectedOrder(null);
    setIsCreatingOrder(false);
    setSelectedAuditLog(null);
  }

  function handleEditClient(client: Client) {
    setActiveSection("clients");
    setEditingClient(client);
    setSelectedClient(null);
    setSelectedOrder(null);
    setIsCreatingOrder(false);
    setSelectedAuditLog(null);
  }

  function handleClientSaved(client: Client) {
    setEditingClient(null);
    setSelectedClient(client);
  }

  function handleViewAuditLog(log: AuditLog) {
    setActiveSection("audit");
    setSelectedAuditLog(log);
    setSelectedOrder(null);
    setIsCreatingOrder(false);
    setSelectedClient(null);
    setEditingClient(null);
  }

  function handleCreateOrder() {
    setActiveSection("orders");
    setIsCreatingOrder(true);
    setSelectedOrder(null);
    setSelectedClient(null);
    setEditingClient(null);
    setSelectedAuditLog(null);
  }

  function handleOrderCreated(order: ServiceOrder) {
    setIsCreatingOrder(false);
    handleViewOrder(order);
  }

  useEffect(() => {
    refreshNotifications();
  }, []);

  useEffect(() => {
    if (!isNotificationsOpen) {
      return;
    }

    function handleDocumentMouseDown(event: MouseEvent) {
      if (!notificationPanelRef.current?.contains(event.target as Node)) {
        setIsNotificationsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleDocumentMouseDown);
    return () => document.removeEventListener("mousedown", handleDocumentMouseDown);
  }, [isNotificationsOpen]);

  async function refreshNotifications() {
    try {
      setIsLoadingNotifications(true);
      setNotificationError(null);
      const nextNotifications = await listNotifications();
      setNotifications(nextNotifications);
      setSelectedNotification((current) =>
        current ? nextNotifications.find((notification) => notification.id === current.id) ?? null : null,
      );
    } catch (loadError) {
      setNotificationError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar as notificacoes.");
    } finally {
      setIsLoadingNotifications(false);
    }
  }

  async function handleNotificationButtonClick() {
    const nextOpenState = !isNotificationsOpen;
    setIsNotificationsOpen(nextOpenState);

    if (nextOpenState) {
      await refreshNotifications();
    }
  }

  async function handleNotificationSelect(notification: Notification) {
    setSelectedNotification(notification);
    setNotificationError(null);

    try {
      setIsLoadingNotificationDetail(true);
      const detail = await getNotification(notification.id);
      setSelectedNotification(detail);
      setNotifications((current) => current.map((item) => (item.id === detail.id ? detail : item)));
    } catch (loadError) {
      setNotificationError(loadError instanceof Error ? loadError.message : "Nao foi possivel abrir a notificacao.");
    } finally {
      setIsLoadingNotificationDetail(false);
    }
  }

  function renderContent() {
    if (selectedAuditLog) {
      return <AuditLogDetailPage log={selectedAuditLog} onBack={() => setSelectedAuditLog(null)} />;
    }

    if (editingClient) {
      return (
        <ClientEditPage
          client={editingClient}
          onCancel={() => {
            setEditingClient(null);
            setSelectedClient(editingClient);
          }}
          onSaved={handleClientSaved}
        />
      );
    }

    if (selectedClient) {
      return (
        <ClientDetailPage
          client={selectedClient}
          canViewFinance={user.perfil === "FINANCEIRO"}
          onEdit={handleEditClient}
          onBack={() => setSelectedClient(null)}
        />
      );
    }

    if (selectedOrder) {
      return <ServiceOrderDetailPage order={selectedOrder} onBack={() => setSelectedOrder(null)} />;
    }

    if (isCreatingOrder) {
      return <ServiceOrderCreatePage onCancel={() => setIsCreatingOrder(false)} onCreated={handleOrderCreated} />;
    }

    if (activeSection === "orders") {
      return <ServiceOrdersPage onCreateOrder={handleCreateOrder} onViewOrder={handleViewOrder} />;
    }

    if (activeSection === "finance") {
      return <FinanceReceivablesPage />;
    }

    if (activeSection === "clients") {
      return <ClientsPage onEditClient={handleEditClient} onViewClient={handleViewClient} />;
    }

    if (activeSection === "audit") {
      return <AuditLogsPage onViewLog={handleViewAuditLog} />;
    }

    if (activeSection === "users") {
      return <AdminUsersPage />;
    }

    if (activeSection === "delegations") {
      return <AdminDelegationsPage />;
    }

    return getContent(activeSection);
  }

  function openProfileDialog() {
    setProfileForm({
      name: user.name,
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    });
    setProfileError(null);
    setProfileSuccess(null);
    setIsUserMenuOpen(false);
    setIsProfileDialogOpen(true);
  }

  async function handleProfileSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setProfileError(null);
    setProfileSuccess(null);

    const trimmedName = profileForm.name.trim();
    const wantsPasswordChange = profileForm.currentPassword || profileForm.newPassword || profileForm.confirmPassword;

    if (!trimmedName) {
      setProfileError("Indique o nome do utilizador.");
      return;
    }

    if (wantsPasswordChange) {
      if (!profileForm.currentPassword || !profileForm.newPassword || !profileForm.confirmPassword) {
        setProfileError("Preencha a password atual, a nova password e a confirmação.");
        return;
      }

      if (profileForm.newPassword !== profileForm.confirmPassword) {
        setProfileError("A confirmação da nova password não coincide.");
        return;
      }
    }

    try {
      setIsSavingProfile(true);

      let updatedUser = user;
      if (trimmedName !== user.name) {
        const profile = await updateOwnProfile({ nome: trimmedName });
        updatedUser = {
          ...user,
          initials: getInitials(profile.nome),
          name: profile.nome,
        };
        onUserUpdated(updatedUser);
      }

      if (wantsPasswordChange) {
        await changeOwnPassword({
          currentPassword: profileForm.currentPassword,
          newPassword: profileForm.newPassword,
        });
        setProfileForm((current) => ({
          ...current,
          currentPassword: "",
          newPassword: "",
          confirmPassword: "",
        }));
      }

      setProfileForm((current) => ({ ...current, name: updatedUser.name }));
      setIsProfileDialogOpen(false);
    } catch (saveError) {
      setProfileError(saveError instanceof Error ? saveError.message : "Não foi possível guardar as alterações.");
    } finally {
      setIsSavingProfile(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="app-sidebar" aria-label="Menu principal">
        <div className="sidebar-brand">
          <strong>Associação Agrícola</strong>
          <span>{user.delegation}</span>
        </div>

        <nav className="sidebar-nav">
          {menuItems
            .filter((item) => !item.adminOnly || user.perfil === "ADMINISTRADOR")
            .map((item) => {
            const Icon = item.icon;

            return (
              <button
                className={`sidebar-link${activeSection === item.id ? " sidebar-link-active" : ""}`}
                key={item.id}
                type="button"
                onClick={() => handleSectionChange(item.id)}
              >
                <Icon aria-hidden="true" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-user">
          <button
            className="sidebar-user-trigger"
            type="button"
            aria-expanded={isUserMenuOpen}
            aria-haspopup="menu"
            onClick={() => setIsUserMenuOpen((current) => !current)}
          >
            <span className="avatar">{user.initials}</span>
            <span className="sidebar-user-copy">
              <strong>{user.name}</strong>
              <small>{user.role}</small>
            </span>
          </button>
          {isUserMenuOpen ? (
            <div className="sidebar-user-menu" role="menu">
              <button type="button" role="menuitem" onClick={openProfileDialog}>
                Alterar perfil
              </button>
              <button type="button" role="menuitem" onClick={onLogout}>
                Terminar sessão
              </button>
            </div>
          ) : null}
          <button className="logout-button" type="button" aria-label="Terminar sessão" onClick={onLogout}>
            <LogoutIcon aria-hidden="true" />
          </button>
        </div>
      </aside>

      <section className="app-main">
        <header className="app-header">
          <div>
            <h1>{pageTitle}</h1>
          </div>

          <div className="header-actions">
            <div className="notification-menu" ref={notificationPanelRef}>
              <button
                className="notification-button"
                type="button"
                aria-label="Notificacoes"
                aria-expanded={isNotificationsOpen}
                aria-haspopup="dialog"
                onClick={handleNotificationButtonClick}
              >
                <BellIcon aria-hidden="true" />
                {unreadNotificationsCount > 0 ? <span>{unreadNotificationsCount > 99 ? "99+" : unreadNotificationsCount}</span> : null}
              </button>

              {isNotificationsOpen ? (
                <div className="notification-panel" role="dialog" aria-label="Notificacoes">
                  <div className="notification-panel-header">
                    <div>
                      <strong>Notificacoes</strong>
                      <small>{unreadNotificationsCount} por ler</small>
                    </div>
                    <button type="button" onClick={refreshNotifications} disabled={isLoadingNotifications}>
                      Atualizar
                    </button>
                  </div>

                  {notificationError ? <div className="notification-error">{notificationError}</div> : null}

                  {isLoadingNotifications ? (
                    <div className="notification-empty">A carregar...</div>
                  ) : notifications.length === 0 ? (
                    <div className="notification-empty">
                      <strong>Tudo limpo</strong>
                      <span>Nao existem notificacoes para mostrar.</span>
                    </div>
                  ) : (
                    <div className="notification-panel-body">
                      <div className="notification-list" role="list">
                        {notifications.map((notification) => (
                          <button
                            className={`notification-item${notification.lida ? "" : " notification-item-unread"}${selectedNotification?.id === notification.id ? " notification-item-active" : ""}`}
                            key={notification.id}
                            type="button"
                            onClick={() => handleNotificationSelect(notification)}
                          >
                            <span className="notification-item-title">{notification.titulo}</span>
                            <span className="notification-item-message">{notification.mensagem}</span>
                            <span className="notification-item-date">{formatNotificationDate(notification.createdAt)}</span>
                          </button>
                        ))}
                      </div>

                      <div className="notification-detail">
                        {selectedNotification ? (
                          <>
                            <div className="notification-detail-header">
                              <strong>{selectedNotification.titulo}</strong>
                              <span>{formatNotificationDate(selectedNotification.createdAt)}</span>
                            </div>
                            <p>{selectedNotification.mensagem}</p>
                            <dl>
                              <div>
                                <dt>Evento</dt>
                                <dd>{selectedNotification.evento || "-"}</dd>
                              </div>
                              <div>
                                <dt>Canal</dt>
                                <dd>{selectedNotification.canal}</dd>
                              </div>
                              <div>
                                <dt>Estado</dt>
                                <dd>{selectedNotification.lida ? "Lida" : "Por ler"}</dd>
                              </div>
                            </dl>
                            <pre>{formatNotificationPayload(selectedNotification.payload)}</pre>
                            {isLoadingNotificationDetail ? <span className="notification-detail-loading">A atualizar detalhe...</span> : null}
                          </>
                        ) : (
                          <div className="notification-empty">Selecione uma notificacao para ver o detalhe.</div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          </div>
        </header>

        {renderContent()}
      </section>

      {isProfileDialogOpen ? (
        <div className="profile-dialog-backdrop" role="presentation">
          <form className="profile-dialog" onSubmit={handleProfileSubmit}>
            <div className="profile-dialog-header">
              <h2>Alterar perfil</h2>
              <button type="button" aria-label="Fechar" onClick={() => setIsProfileDialogOpen(false)}>
                x
              </button>
            </div>

            {profileError ? <div className="login-alert login-alert-error">{profileError}</div> : null}
            {profileSuccess ? <div className="login-alert login-alert-success">{profileSuccess}</div> : null}

            <label className="field">
              Nome
              <input
                value={profileForm.name}
                onChange={(event) => setProfileForm((current) => ({ ...current, name: event.target.value }))}
              />
            </label>

            <div className="profile-dialog-section">
              <h3>Password</h3>
              <label className="field">
                Password atual
                <input
                  type="password"
                  autoComplete="current-password"
                  value={profileForm.currentPassword}
                  onChange={(event) => setProfileForm((current) => ({ ...current, currentPassword: event.target.value }))}
                />
              </label>
              <label className="field">
                Nova password
                <input
                  type="password"
                  autoComplete="new-password"
                  value={profileForm.newPassword}
                  onChange={(event) => setProfileForm((current) => ({ ...current, newPassword: event.target.value }))}
                />
              </label>
              <label className="field">
                Confirmar nova password
                <input
                  type="password"
                  autoComplete="new-password"
                  value={profileForm.confirmPassword}
                  onChange={(event) => setProfileForm((current) => ({ ...current, confirmPassword: event.target.value }))}
                />
              </label>
            </div>

            <div className="profile-dialog-actions">
              <button type="button" className="clear-button" onClick={() => setIsProfileDialogOpen(false)}>
                Cancelar
              </button>
              <button type="submit" className="primary-action" disabled={isSavingProfile}>
                {isSavingProfile ? "A guardar..." : "Guardar"}
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </main>
  );
}

function getInitials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");
}

function formatNotificationDate(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatNotificationPayload(payload: unknown) {
  if (!payload || (typeof payload === "object" && !Object.keys(payload).length)) {
    return "{}";
  }

  return JSON.stringify(payload, null, 2);
}
