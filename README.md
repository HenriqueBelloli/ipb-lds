# ERP Associação Agrícola — LDS Grupo 1

Sistema ERP Web centralizado para uma associação agrícola com 9 delegações regionais. Resolve login partilhado sem rastreabilidade, dados dispersos pelas delegações e consolidação financeira manual em Excel.

---

## Arquitetura

### Visão geral

O sistema segue uma arquitetura de **microserviços** com um único ponto de entrada externo (nginx). Cada serviço tem a sua própria base de dados PostgreSQL e comunica de forma assíncrona via RabbitMQ (eventos) ou síncrona via HTTP interno.

```
                         ┌──────────────────────────────────────────────┐
Cliente (browser/Postman)│              nginx  :80                      │
          ──────────────►│  /api/auth/        → auth-service      :8001  │
                         │  /api/usuarios/    → usuario-service   :8002  │
                         │  /api/clientes/    → cliente-service   :8003  │
                         │  /api/servicos/    → servico-service   :8004  │
                         │  /api/ordens/      → os-service        :8005  │
                         │  /api/financeiro/  → financeiro-service:8006  │
                         │  /api/auditoria/   → auditoria-service :8008  │
                         │  /api/notificacoes/→ notification-svc  :8009  │
                         └──────────────────────────────────────────────┘
                                             │
                         ┌───────────────────▼───────────────────────────┐
                         │           RabbitMQ  :5672  (exchange: topic)  │
                         └───────────────────────────────────────────────┘
```

### Serviços implementados

| Serviço | Porta | Responsabilidade |
|---|---|---|
| auth-service | 8001 | Login, JWT, refresh token, logout |
| usuario-service | 8002 | Utilizadores, delegações, perfis RBAC |
| cliente-service | 8003 | Clientes, associados, verificação de inadimplência |
| servico-service | 8004 | Catálogo de serviços e preços por delegação |
| os-service | 8005 | Ordens de serviço, estados, histórico |
| financeiro-service | 8006 | Contas a receber, pagamentos, mensalidades |
| auditoria-service | 8008 | Registo de auditoria — consumidor de eventos |
| notification-service | 8009 | Alertas internos — consumidor de eventos |

> `conciliacao-service` (porta 8007) foi desativado no âmbito desta entrega.

### Infraestrutura de suporte

| Container | Porta(s) | Função |
|---|---|---|
| nginx | 80 | Reverse proxy — único ponto de entrada |
| RabbitMQ | 5672 / 15672 | Mensageria assíncrona; painel em :15672 |
| PostgreSQL (×8) | — | Uma instância isolada por serviço |
| MailHog | 1025 / 8025 | SMTP stub de desenvolvimento; UI em :8025 |

### Autenticação e RBAC

O `auth-service` emite tokens JWT com os claims `usuarioId`, `delegacaoId` e `perfil`. Todos os outros serviços validam o token localmente via `shared/auth_middleware/drf_authentication.py` (sem chamada ao auth-service por request).

Perfis disponíveis (hierarquia crescente):

```
OPERADOR → GESTOR → FINANCEIRO → DIRECAO → ADMINISTRADOR
```

### Estrutura de pastas

```
sdl-project-group-01/
├── backend/
│   ├── shared/                  ← middleware JWT e RabbitMQ partilhados
│   ├── auth_service/
│   ├── usuario_service/
│   ├── cliente_service/
│   ├── servico_service/
│   ├── os_service/
│   ├── financeiro_service/
│   ├── auditoria_service/
│   └── notification_service/
├── reverse-proxy/
│   └── nginx.conf
├── postman/
│   ├── ERP_Associacao_Agricola.postman_collection.json
│   └── ldsgrupo1-local.postman_environment.json
├── docker-compose.yml           ← produção/CI (usa imagens do registry)
├── docker-compose.override.yml  ← desenvolvimento local (build a partir do código)
└── .env.example
```

---

## Setup

### Pré-requisitos

- Docker Desktop ≥ 24 com Docker Compose v2
- Git

### 1. Clonar o repositório

```bash
git clone <url-do-repositório>
cd sdl-project-group-01
```

### 2. Criar o ficheiro de ambiente

```bash
cp .env.example .env
```

O `.env` na raiz é partilhado por todos os serviços. As variáveis `DB_HOST` e `DB_NAME` são injetadas individualmente pelo `docker-compose.yml` — não é necessário editar manualmente.

Para desenvolvimento local os valores padrão do `.env.example` funcionam sem alteração. Em produção, altere pelo menos:

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave Django (única por ambiente) |
| `JWT_SECRET_KEY` | Chave de assinatura JWT — **igual em todos os serviços** |
| `DB_PASSWORD` | Password do PostgreSQL |
| `INTERNAL_SERVICE_SECRET` | Segredo para chamadas sistema-a-sistema |

---

## Execução

### Desenvolvimento local (build a partir do código)

O `docker-compose.override.yml` é lido automaticamente pelo Docker Compose e activa o build local para todos os serviços.

```bash
# Primeira execução — compila todas as imagens e inicia
docker compose up --build -d

# Execuções seguintes (sem alterações de código)
docker compose up -d
```

Aguarde ~60 s até todos os health checks ficarem `healthy`:

```bash
docker compose ps
```

### Parar / limpar

```bash
# Parar sem apagar dados
docker compose down

# Parar e apagar volumes (base de dados incluída)
docker compose down -v
```

### Criar utilizador administrador (seed)

```bash
docker exec ldsgrupo1_auth python manage.py seed
```

O comando cria uma delegação e um utilizador administrador com as credenciais:

```
email:    admin@ldsgrupo1.pt
password: Admin123!
```

### URLs úteis após `docker compose up`

| Serviço | URL |
|---|---|
| API (via nginx) | http://localhost |
| RabbitMQ Management | http://localhost:15672 (guest / guest) |
| MailHog UI | http://localhost:8025 |
| Swagger — auth | http://localhost:8001/api/docs/ |
| Swagger — usuarios | http://localhost:8002/api/docs/ |
| Swagger — clientes | http://localhost:8003/api/docs/ |
| Swagger — servicos | http://localhost:8004/api/docs/ |
| Swagger — ordens | http://localhost:8005/api/docs/ |
| Swagger — financeiro | http://localhost:8006/api/docs/ |
| Swagger — auditoria | http://localhost:8008/api/docs/ |
| Swagger — notificacoes | http://localhost:8009/api/docs/ |

---

## Testes

Cada serviço tem uma suite de testes unitários/integração em `backend/<serviço>/app/<app>/tests.py`.

### Executar testes de um serviço

```bash
# Exemplo: auth-service
docker exec ldsgrupo1_auth python manage.py test authentication --verbosity=2

# usuario-service
docker exec ldsgrupo1_usuario python manage.py test usuarios --verbosity=2

# cliente-service
docker exec ldsgrupo1_cliente python manage.py test clientes --verbosity=2

# servico-service
docker exec ldsgrupo1_servico python manage.py test servicos --verbosity=2

# os-service
docker exec ldsgrupo1_os python manage.py test ordens --verbosity=2

# financeiro-service
docker exec ldsgrupo1_financeiro python manage.py test financeiro --verbosity=2

# auditoria-service
docker exec ldsgrupo1_auditoria python manage.py test auditoria --verbosity=2

# notification-service
docker exec ldsgrupo1_notification python manage.py test notifications --verbosity=2
```

### Executar todos os serviços de uma vez

```bash
for svc in auth usuario cliente servico os financeiro auditoria notification; do
  echo "=== $svc ==="
  docker exec ldsgrupo1_${svc} python manage.py test --verbosity=1 2>&1 | tail -3
done
```

### Logs e debugging

```bash
# Seguir logs de um serviço
docker logs -f ldsgrupo1_auth

# Shell Django interativo
docker exec -it ldsgrupo1_auth python manage.py shell

# Aceder à base de dados
docker exec -it ldsgrupo1_db_auth psql -U postgres -d auth_db
```

---

## Testes de API — Postman

### Ficheiros incluídos

| Ficheiro | Descrição |
|---|---|
| `postman/ERP_Associacao_Agricola.postman_collection.json` | Coleção unificada com todos os endpoints |
| `postman/ldsgrupo1-local.postman_environment.json` | Ambiente local (`base_url = http://localhost`) |

### Importar no Postman

1. Abrir o Postman
2. **Import** → seleccionar `ERP_Associacao_Agricola.postman_collection.json`
3. **Import** → seleccionar `ldsgrupo1-local.postman_environment.json`
4. Activar o ambiente **ldsgrupo1 — Local** no selector do canto superior direito

### Fluxo de autenticação

A coleção está configurada para gerir os tokens automaticamente:

1. Expandir a pasta **Auth Service**
2. Executar **Login** — o script de teste guarda `access_token` e `refresh_token` nas variáveis de ambiente
3. Todas as outras requests herdam o `Bearer {{access_token}}` definido ao nível da coleção

> As credenciais pré-configuradas na coleção são `admin@ldsgrupo1.pt` / `Admin123!` (criadas pelo comando `seed`).

### Fluxo de teste recomendado

```
1. Auth → Login                       (guarda tokens)
2. Usuarios → Listar Delegações       (verifica RBAC)
3. Usuarios → Criar Utilizador        (cria operador para testes)
4. Clientes → Criar Cliente           (base para OS)
5. Servicos → Criar Serviço           (catálogo)
6. Servicos → Configurar em Delegação (preços)
7. Ordens → Criar OS                  (encadeia clientes + serviços)
8. Ordens → Transicionar Estado       (ORCAMENTO → AGUARDA_APROVACAO → ...)
9. Financeiro → Registar Pagamento    (baixa de duplicata)
10. Notificações → Listar             (verifica eventos recebidos)
```

### Variáveis de ambiente disponíveis

| Variável | Preenchida por | Uso |
|---|---|---|
| `base_url` | Ficheiro de ambiente | `http://localhost` |
| `access_token` | Script do Login | Bearer token nas requests |
| `refresh_token` | Script do Login | Endpoint de refresh |
| `usuario_id` | Manual | Filtros por utilizador |
| `delegacao_id` | Manual | Filtros por delegação |

---

## CI/CD — Pipeline GitLab

Pipeline definido em `.gitlab-ci.yml` com 5 stages: `build → push → deploy-develop → deploy-staging → deploy-production`.

### Branches e ambientes

| Branch | Deploy | Ambiente | Path na VM |
|---|---|---|---|
| `develop` | Automático | develop | `/opt/erp/develop` |
| `staging` | Automático | staging | `/opt/erp/staging` |
| `main` | Manual (aprovação) | production | `/opt/erp/production` |

### Variáveis obrigatórias no GitLab

Configurar em **Settings → CI/CD → Variables**:

| Variável | Tipo | Descrição |
|---|---|---|
| `SSH_PRIVATE_KEY` | File (Protected) | Chave privada SSH para acesso à VM |
| `SSH_HOST` | Variable | IP da VM de deploy |
| `SSH_USER` | Variable | Utilizador SSH (ex: `ubuntu`) |
| `DEVELOP_ENV` | File | Conteúdo do `.env` do ambiente develop |
| `STAGING_ENV` | File | Conteúdo do `.env` do ambiente staging |
| `PRODUCTION_ENV` | File | Conteúdo do `.env` de produção |

> `CI_REGISTRY`, `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD` e `CI_REGISTRY_IMAGE` são preenchidas automaticamente pelo GitLab.
