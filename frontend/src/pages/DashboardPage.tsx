import { useState } from "react";
import { AppUser } from "../App";
import { ServiceOrdersPage } from "./ServiceOrdersPage";
import {
  BellIcon,
  ClipboardIcon,
  FileIcon,
  HomeIcon,
  LogoutIcon,
  MoneyIcon,
  UsersIcon,
} from "../shared/icons";

type DashboardPageProps = {
  user: AppUser;
  onLogout: () => void;
};

type AppSection = "dashboard" | "orders" | "finance" | "clients" | "audit";

const menuItems = [
  { id: "dashboard", label: "Dashboard", icon: HomeIcon },
  { id: "orders", label: "Ordens de Serviço", icon: ClipboardIcon },
  { id: "finance", label: "Financeiro", icon: MoneyIcon },
  { id: "clients", label: "Clientes", icon: UsersIcon },
  { id: "audit", label: "Auditoria", icon: FileIcon },
] satisfies Array<{
  id: AppSection;
  label: string;
  icon: typeof HomeIcon;
}>;

const sectionTitles: Record<AppSection, string> = {
  dashboard: "Dashboard — Visão Geral",
  orders: "Ordens de Serviço",
  finance: "Financeiro",
  clients: "Clientes",
  audit: "Auditoria",
};

const emptySectionLabels: Record<AppSection, string> = {
  dashboard: "Conteúdo inicial vazio",
  orders: "Ordens de Serviço",
  finance: "Área financeira vazia",
  clients: "Área de clientes vazia",
  audit: "Área de auditoria vazia",
};

const emptySectionTitles: Record<AppSection, string> = {
  dashboard: "",
  orders: "",
  finance: "Financeiro",
  clients: "Clientes",
  audit: "Auditoria",
};

const emptySectionCopy: Record<AppSection, string> = {
  dashboard: "",
  orders: "",
  finance: "Este módulo será implementado a seguir.",
  clients: "Este módulo será implementado a seguir.",
  audit: "Este módulo será implementado a seguir.",
};

const contentFor = {
  dashboard: null,
  orders: <ServiceOrdersPage />,
  finance: null,
  clients: null,
  audit: null,
};

function EmptyWorkspace({ section }: { section: AppSection }) {
  if (section === "dashboard") {
    return <div className="empty-workspace" aria-label={emptySectionLabels[section]} />;
  }

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

export function DashboardPage({ user, onLogout }: DashboardPageProps) {
  const [activeSection, setActiveSection] = useState<AppSection>("dashboard");

  const pageTitle = sectionTitles[activeSection];

  return (
    <main className="app-shell">
      <aside className="app-sidebar" aria-label="Menu principal">
        <div className="sidebar-brand">
          <strong>Associação Agrícola</strong>
          <span>{user.delegation}</span>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                className={`sidebar-link${activeSection === item.id ? " sidebar-link-active" : ""}`}
                key={item.id}
                type="button"
                onClick={() => setActiveSection(item.id)}
              >
                <Icon aria-hidden="true" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-user">
          <span className="avatar">{user.initials}</span>
          <span className="sidebar-user-copy">
            <strong>{user.name}</strong>
            <small>{user.role}</small>
          </span>
          <button className="logout-button" type="button" aria-label="Terminar sessão" onClick={onLogout}>
            <LogoutIcon aria-hidden="true" />
          </button>
        </div>
      </aside>

      <section className="app-main">
        <header className="app-header">
          <div>
            <h1>{pageTitle}</h1>
            <p>
              {user.delegation} · {user.email}
            </p>
          </div>

          <div className="header-actions">
            <button className="notification-button" type="button" aria-label="Notificações">
              <BellIcon aria-hidden="true" />
              <span>3</span>
            </button>
            <span className="header-divider" />
            <span className="avatar avatar-header">{user.initials}</span>
          </div>
        </header>

        {getContent(activeSection)}
      </section>
    </main>
  );
}
