# CLAUDE.md — Contexto Completo do Projeto ERP Associação Agrícola

## Visão Geral do Projeto

Sistema ERP Web centralizado para uma associação agrícola com 9 delegações regionais. O sistema resolve problemas críticos de fragmentação de dados, ausência de rastreabilidade de lançamentos, controlo financeiro manual e falta de indicadores de gestão.

### Problema que o sistema resolve

- Login partilhado no software atual (XD Software) — sem rastreabilidade de quem lançou o quê e em que delegação
- Dados dispersos pelas 9 delegações sem repositório central
- Consolidação financeira manual feita em Excel por um único colaborador
- Sem gestão estruturada de ordens de serviço
- Sem indicadores operacionais e financeiros em tempo real

### Solução

WebApp central com arquitetura de microserviços, onde cada delegação acede com credenciais individuais. Todos os registos ficam marcados com utilizador, delegação e timestamp. Módulos de cadastros, ordens de serviço, financeiro e conciliação bancária.

---

## Stack Tecnológica

| Componente | Tecnologia | Versão |
|---|---|---|
| Backend | Django REST Framework | Django 4.2+ |
| Autenticação | djangorestframework-simplejwt | latest |
| Base de dados | PostgreSQL | 15 |
| Mensageria | RabbitMQ | 3.12 |
| Containerização | Docker + Docker Compose | latest |
| Reverse Proxy | nginx | latest |
| Frontend | React | 18+ |
| Documentação API | drf-spectacular (OpenAPI/Swagger) | latest |

---

## Arquitetura — Microserviços

### Microserviços a Implementar (8)

| # | Serviço | Porta | Tipo | Responsabilidade |
|---|---|---|---|---|
| 1 | auth-service | 8001 | Suporte | Login, JWT, refresh token |
| 2 | usuario-service | 8002 | Suporte | Utilizadores, delegações, perfis RBAC |
| 3 | cliente-service | 8003 | Core | Clientes, associados, verificação inadimplência |
| 4 | servico-service | 8004 | Core | Catálogo de serviços e preços por delegação |
| 5 | os-service | 8005 | Core | Ordens de serviço, estados, histórico |
| 6 | financeiro-service | 8006 | Core | Contas a receber, pagamentos, mensalidades |
| 7 | conciliacao-service | 8007 | Core | Importação bancária, conciliação automática e manual |
| 8 | notification-service | 8008 | Suporte | Consumidor de eventos RabbitMQ, alertas internos |

### Infraestrutura de Suporte

- **nginx** — reverse proxy, único ponto de entrada externo
- **RabbitMQ** — mensageria assíncrona entre serviços
- **PostgreSQL** — uma instância por microserviço (isolamento total)

### Roteamento nginx

```
/api/auth/       → auth-service:8001
/api/usuarios/   → usuario-service:8002
/api/clientes/   → cliente-service:8003
/api/servicos/   → servico-service:8004
/api/ordens/     → os-service:8005
/api/financeiro/ → financeiro-service:8006
/api/conciliacao/→ conciliacao-service:8007
/api/notificacoes/→ notification-service:8008
/                → frontend:3000
```

---

## Estrutura de Pastas

```
projeto-erp/
├── backend/
│   ├── auth-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── app/
│   │       ├── manage.py
│   │       ├── core/          # settings, urls, wsgi
│   │       └── authentication/# models, views, serializers, urls
│   ├── usuario-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── app/
│   │       ├── manage.py
│   │       ├── core/
│   │       └── usuarios/
│   ├── cliente-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── app/
│   │       ├── manage.py
│   │       ├── core/
│   │       └── clientes/
│   ├── servico-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── app/
│   │       ├── manage.py
│   │       ├── core/
│   │       └── servicos/
│   ├── os-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── app/
│   │       ├── manage.py
│   │       ├── core/
│   │       └── ordens/
│   ├── financeiro-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── app/
│   │       ├── manage.py
│   │       ├── core/
│   │       └── financeiro/
│   ├── conciliacao-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── app/
│   │       ├── manage.py
│   │       ├── core/
│   │       └── conciliacao/
│   └── notification-service/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── .env.example
│       └── app/
│           ├── manage.py
│           ├── core/
│           └── notifications/
├── docs/
│   ├── architecture.md
│   └── diagrams/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── .env.example
│   └── src/
├── reverse-proxy/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── nginx.dev.conf
├── postman/
│   └── ERP_Associacao.postman_collection.json
├── docker-compose.yml
├── docker-compose.staging.yml
├── docker-compose.prod.yml
├── .gitlab-ci.yml
├── .gitignore
└── README.md
```

---

## Modelos de Dados (Entidades)

### auth-service / usuario-service

```python
# Usuario
id: UUID (PK)
nome: CharField
email: EmailField (unique)
passwordHash: CharField
perfil: CharField (choices: OPERADOR, GESTOR, FINANCEIRO, DIRECAO, ADMINISTRADOR)
delegacaoId: UUID (FK → Delegacao)
ativo: BooleanField (default=True)
createdAt: DateTimeField (auto)

# Delegacao
id: UUID (PK)
codigo: CharField (unique)
nome: CharField
localizacao: CharField
responsavelId: UUID (FK → Usuario, nullable)
```

### cliente-service

```python
# Cliente
id: UUID (PK)
nif: CharField (unique)
nome: CharField
telefone: CharField (nullable)
email: EmailField (nullable)
morada: CharField (nullable)
flagAssociado: BooleanField (default=False)
ativo: BooleanField (default=True)
createdAt: DateTimeField (auto)

# ClienteDelegacao
id: UUID (PK)
clienteId: UUID (FK → Cliente)
delegacaoId: UUID (external reference — not FK, stored as UUID)
```

### servico-service

```python
# Servico
id: UUID (PK)
nome: CharField
descricao: TextField (nullable)
flagBonificavel: BooleanField (default=False)
ativo: BooleanField (default=True)

# ServicoDelegacao
id: UUID (PK)
servicoId: UUID (FK → Servico)
delegacaoId: UUID (external reference)
precoAssociado: DecimalField
precoNaoAssociado: DecimalField
percentualEntrada: DecimalField (0-100, default=0)
ativo: BooleanField (default=True)
```

### os-service

```python
# OrdemServico
id: UUID (PK)
clienteId: UUID (external reference)
delegacaoContratacaoId: UUID (external reference)
delegacaoExecucaoId: UUID (external reference)
usuarioCriacaoId: UUID (external reference)
status: CharField (choices: ORCAMENTO, AGUARDA_APROVACAO, PAGAMENTO_PENDENTE,
                            A_EXECUTAR, EM_EXECUCAO, CONCLUIDO, FATURADO, CANCELADO)
valorTotal: DecimalField
tipoPreco: CharField (choices: ASSOCIADO, NAO_ASSOCIADO)
motivoCancelamento: TextField (nullable)
createdAt: DateTimeField (auto)
updatedAt: DateTimeField (auto)

# OrdemServicoServico
id: UUID (PK)
ordemServicoId: UUID (FK → OrdemServico)
servicoId: UUID (external reference)
servicoDelegacaoId: UUID (external reference)
precoAplicado: DecimalField
bonificado: BooleanField (default=False)

# OrdemServicoHistorico
id: UUID (PK)
ordemServicoId: UUID (FK → OrdemServico)
usuarioId: UUID (external reference)
statusAnterior: CharField (nullable)
statusNovo: CharField
observacao: TextField (nullable)
createdAt: DateTimeField (auto)
```

### financeiro-service

```python
# ContaReceber
id: UUID (PK)
clienteId: UUID (external reference)
ordemServicoId: UUID (external reference, nullable — mensalidades não têm OS)
tipo: CharField (choices: ENTRADA, SALDO_FINAL, MENSALIDADE)
valor: DecimalField
valorPago: DecimalField (default=0)
status: CharField (choices: ABERTA, PARCIAL, PAGA, VENCIDA)
dataVencimento: DateField
createdAt: DateTimeField (auto)

# Pagamento
id: UUID (PK)
contaReceberId: UUID (FK → ContaReceber)
usuarioId: UUID (external reference)
valor: DecimalField
data: DateField
referenciaBancaria: CharField (nullable)

# ConfiguracaoFinanceira
id: UUID (PK)
chave: CharField (unique)
valor: CharField
atualizadoEm: DateTimeField (auto)
usuarioId: UUID (external reference)
```

### conciliacao-service

```python
# ImportacaoBancaria
id: UUID (PK)
usuarioId: UUID (external reference)
nomeFicheiro: CharField
formato: CharField (choices: OFX, CSV)
totalRegistos: IntegerField
createdAt: DateTimeField (auto)

# MovimentoBancario
id: UUID (PK)
importacaoId: UUID (FK → ImportacaoBancaria)
dataMovimento: DateField
valor: DecimalField
descricao: CharField
referenciaBanco: CharField
status: CharField (choices: POR_CONCILIAR, CONCILIADO, IGNORADO)
createdAt: DateTimeField (auto)

# Conciliacao
id: UUID (PK)
movimentoBancarioId: UUID (FK → MovimentoBancario)
pagamentoId: UUID (external reference)
tipo: CharField (choices: AUTOMATICO, MANUAL)
usuarioId: UUID (external reference, nullable — automático não tem utilizador)
createdAt: DateTimeField (auto)
```

### notification-service

```python
# Notificacao
id: UUID (PK)
tipo: CharField
evento: CharField
payload: JSONField
lida: BooleanField (default=False)
createdAt: DateTimeField (auto)
```

---

## Perfis e RBAC

### Perfis disponíveis

```python
PERFIS = [
    'OPERADOR',       # Cria e gere OS e clientes da sua delegação
    'GESTOR',         # Acesso completo à sua delegação + leitura consolidada
    'FINANCEIRO',     # Acesso completo ao módulo financeiro de todas as delegações
    'DIRECAO',        # Leitura total — todos os módulos e delegações
    'ADMINISTRADOR',  # Configuração do sistema — utilizadores, delegações
]
```

### Autenticação JWT — shared/auth_middleware/

Cada microserviço valida o JWT localmente. O token contém:

```json
{
  "usuarioId": "uuid",
  "delegacaoId": "uuid",
  "perfil": "GESTOR",
  "exp": 1234567890
}
```

O módulo `shared/auth_middleware/` contém:
- `drf_authentication.py` — `JWTStatelessAuthentication`: autentica no DRF sem DB lookup (usar em todos os serviços não-auth)
- `permissions.py` — `IsOperador`, `IsGestor`, `IsFinanceiro`, `IsDirecao`, `IsAdministrador`, `IsMesmaDelegacao` (hierarquia numérica via `PERFIL_ORDER`)
- `middleware.py` — `JWTMiddleware`: valida JWT para views Django puras (sem DRF)
- `decorators.py` — `@require_perfil(...)`: protege views Django puras (sem DRF)

**Padrão para serviços DRF** (todos excepto auth-service):

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'shared.auth_middleware.drf_authentication.JWTStatelessAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    ...
}
```

`JWTStatelessAuthentication` valida assinatura e expiração do token, e preenche `request.user` (_JWTUser) e `request.auth` (payload dict) no sistema DRF. `JWTMiddleware` destina-se a views Django puras — não registar no MIDDLEWARE de serviços DRF.

### Regras de acesso por módulo

```
OPERADOR    → Criar/editar OS e clientes da SUA delegação apenas
GESTOR      → Tudo do OPERADOR + preços de serviços + leitura consolidada
FINANCEIRO  → Módulo financeiro de TODAS as delegações + leitura de OS
DIRECAO     → Leitura de tudo — sem criação ou edição
ADMINISTRADOR → Utilizadores, delegações, configurações globais
```

---

## Regras de Negócio Críticas

### 1. Determinação de Preço na Criação de OS

```
Frontend seleciona cliente
    → cliente-service GET /clientes/{id}
    → cliente-service chama financeiro-service GET /contas-receber/inadimplente/{clienteId}
    → financeiro-service verifica: EXISTS ContaReceber WHERE clienteId = X
        AND tipo = MENSALIDADE
        AND status IN ('ABERTA', 'VENCIDA')
        AND EXTRACT(MONTH FROM dataVencimento) = mes_atual
        AND EXTRACT(YEAR FROM dataVencimento) = ano_atual
    → cliente-service retorna: flagAssociado + inadimplente + tipoPreco

tipoPreco = ASSOCIADO apenas se:
    flagAssociado = True AND inadimplente = False

tipoPreco = NAO_ASSOCIADO em qualquer outro caso

Frontend exibe aviso visual se inadimplente mas permite prosseguir
Backend grava tipoPreco na OrdemServico sem segunda validação
```

### 2. State Machine da Ordem de Serviço

```
ORCAMENTO
    ↓ (operador envia para aprovação)
AGUARDA_APROVACAO
    ↓ (cliente aprova — sistema verifica percentualEntrada)
    ├── percentualEntrada > 0 → PAGAMENTO_PENDENTE (gera ContaReceber ENTRADA)
    └── percentualEntrada = 0 → A_EXECUTAR
PAGAMENTO_PENDENTE
    ↓ (financeiro regista pagamento + entrada quitada)
A_EXECUTAR
    ↓ (operador inicia)
EM_EXECUCAO
    ↓ (operador conclui)
CONCLUIDO
    ↓ (financeiro fatura — gera ContaReceber SALDO_FINAL)
FATURADO

CANCELADO ← possível em qualquer estado EXCETO FATURADO
             mas bloqueado se existirem Pagamentos registados
```

### 3. Geração Automática de Mensalidades

```
Job corre no dia 1 de cada mês (Django APScheduler ou Celery Beat)
    → Busca ConfiguracaoFinanceira WHERE chave = 'VALOR_MENSALIDADE'
    → Busca todos os clientes WHERE flagAssociado = True AND ativo = True
    → Para cada cliente:
        → Verifica se já existe ContaReceber WHERE tipo = MENSALIDADE
            AND mesReferencia = mes_atual (evitar duplicado)
        → Se não existe: INSERT ContaReceber (tipo=MENSALIDADE, status=ABERTA,
            dataVencimento=dia 10 do mês)
    → Publica evento: financeiro.mensalidades.geradas
```

### 4. Conciliação Bancária Automática

```
Importar ficheiro OFX ou CSV
    → Para cada linha: INSERT MovimentoBancario (status=POR_CONCILIAR)
    → Executar conciliação automática:
        → Extrair NIF de referenciaBanco
        → GET cliente-service /clientes/nif/{nif}
        → Se cliente encontrado:
            → GET financeiro-service /contas-receber?clienteId=X&valor=Y&status=ABERTA
            → Se exactamente UMA duplicata encontrada:
                → POST financeiro-service /pagamentos (registar pagamento)
                → INSERT Conciliacao (tipo=AUTOMATICO)
                → UPDATE MovimentoBancario status=CONCILIADO
            → Se nenhuma ou múltiplas: permanece POR_CONCILIAR
        → Se cliente não encontrado: permanece POR_CONCILIAR
```

### 5. Baixa de Duplicata (suporte a pagamento parcial)

```
POST /pagamentos {contaReceberId, valor, referenciaBancaria}
    → INSERT Pagamento
    → totalPago = SUM(valor) FROM Pagamento WHERE contaReceberId = X
    → IF totalPago >= contaReceber.valor → UPDATE status = PAGA
    → IF 0 < totalPago < contaReceber.valor → UPDATE status = PARCIAL, valorPago = totalPago
    → IF pagamento é de ENTRADA e status = PAGA:
        → Publica evento: financeiro.pagamento.entrada.confirmado {osId}
```

### 6. Cancelamento de OS

```
PATCH /ordens/{id}/cancelar {motivo}
    → Verifica se status != FATURADO
    → GET financeiro-service /pagamentos?ordemServicoId=X
    → SE existem pagamentos: retorna erro 409
        "Existem pagamentos registados. Regularize no módulo financeiro antes de cancelar."
    → SE não existem: UPDATE status = CANCELADO, motivoCancelamento = motivo
    → INSERT OrdemServicoHistorico
    → Publica evento: os.cancelada
```

---

## Eventos RabbitMQ

### Configuração

```python
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = 5672
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')
EXCHANGE_NAME = 'erp_events'
EXCHANGE_TYPE = 'topic'
```

### Eventos Definidos (mínimo 10 — requisito: 8)

| # | Evento (routing key) | Publicado por | Consumido por | Dados |
|---|---|---|---|---|
| 1 | `auth.login.success` | auth-service | notification-service | {usuarioId, email, timestamp} |
| 2 | `auth.login.failed` | auth-service | notification-service | {email, timestamp} |
| 3 | `usuario.criado` | usuario-service | notification-service | {usuarioId, nome, perfil} |
| 4 | `cliente.criado` | cliente-service | notification-service | {clienteId, nome, nif} |
| 5 | `os.criada` | os-service | notification-service | {osId, clienteId, delegacaoId} |
| 6 | `os.aprovada` | os-service | financeiro-service | {osId, clienteId, itens[], valorTotal} |
| 7 | `os.concluida` | os-service | financeiro-service | {osId, clienteId, valorRestante} |
| 8 | `os.cancelada` | os-service | financeiro-service, notification-service | {osId, motivo} |
| 9 | `financeiro.pagamento.entrada.confirmado` | financeiro-service | os-service | {osId, contaReceberId} |
| 10 | `financeiro.conta.paga` | financeiro-service | notification-service | {contaReceberId, clienteId} |
| 11 | `financeiro.mensalidades.geradas` | financeiro-service | notification-service | {total, mesReferencia} |

### Padrão de Publicação

```python
# publisher.py — reutilizável em todos os serviços
import pika
import json
import os

def publish_event(routing_key: str, data: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.environ.get('RABBITMQ_HOST', 'rabbitmq'),
            port=5672,
            credentials=pika.PlainCredentials(
                os.environ.get('RABBITMQ_USER', 'guest'),
                os.environ.get('RABBITMQ_PASS', 'guest')
            )
        )
    )
    channel = connection.channel()
    channel.exchange_declare(exchange='erp_events', exchange_type='topic', durable=True)
    channel.basic_publish(
        exchange='erp_events',
        routing_key=routing_key,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)  # persistent
    )
    connection.close()
```

### Padrão de Consumo

```python
# consumer.py — base para todos os consumidores
import pika
import json
import threading
import os

def start_consumer(queue_name: str, routing_keys: list, callback):
    def consume():
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.environ.get('RABBITMQ_HOST', 'rabbitmq'))
        )
        channel = connection.channel()
        channel.exchange_declare(exchange='erp_events', exchange_type='topic', durable=True)
        channel.queue_declare(queue=queue_name, durable=True)
        for key in routing_keys:
            channel.queue_bind(exchange='erp_events', queue=queue_name, routing_key=key)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
```

---

## Endpoints REST por Microserviço

### auth-service (:8001)

```
POST   /api/auth/login/          → retorna access + refresh token
POST   /api/auth/refresh/        → renova access token
POST   /api/auth/logout/         → invalida token
```

### usuario-service (:8002)

```
GET    /api/usuarios/            → listar utilizadores
POST   /api/usuarios/            → criar utilizador
GET    /api/usuarios/{id}/       → detalhe
PUT    /api/usuarios/{id}/       → atualizar (inclui campo ativo)
GET    /api/delegacoes/          → listar delegações
POST   /api/delegacoes/          → criar delegação
PUT    /api/delegacoes/{id}/     → atualizar delegação
```

### cliente-service (:8003)

```
GET    /api/clientes/            → listar com filtros: ?nome=&nif=&delegacaoId=&inadimplente=
POST   /api/clientes/            → criar cliente
GET    /api/clientes/{id}/       → detalhe (inclui flagAssociado + inadimplente + tipoPreco)
PUT    /api/clientes/{id}/       → atualizar
GET    /api/clientes/{id}/inadimplente/  → verificação interna (chamado por outros serviços)
POST   /api/clientes/{id}/delegacoes/   → associar a delegação
GET    /api/clientes/{id}/delegacoes/   → listar delegações do cliente
```

### servico-service (:8004)

```
GET    /api/servicos/                        → listar catálogo global
POST   /api/servicos/                        → criar serviço
PUT    /api/servicos/{id}/                   → atualizar (inclui campo ativo)
GET    /api/servicos/delegacao/{delegacaoId}/ → serviços disponíveis com preços
POST   /api/servicos/delegacao/              → configurar serviço numa delegação
PUT    /api/servicos/delegacao/{id}/         → atualizar preços e disponibilidade
```

### os-service (:8005)

```
GET    /api/ordens/              → listar: ?status=&delegacaoId=&clienteId=&periodo=
POST   /api/ordens/              → criar OS
GET    /api/ordens/{id}/         → detalhe
PUT    /api/ordens/{id}/         → atualizar dados
PATCH  /api/ordens/{id}/status/  → transicionar estado
PATCH  /api/ordens/{id}/cancelar/ → cancelar com motivo
GET    /api/ordens/{id}/historico/ → histórico de estados
GET    /api/ordens/delegacao/{delegacaoId}/ → OS por delegação
```

### financeiro-service (:8006)

```
GET    /api/financeiro/contas-receber/          → listar: ?clienteId=&status=&tipo=
GET    /api/financeiro/contas-receber/{id}/     → detalhe
PATCH  /api/financeiro/contas-receber/{id}/faturar/ → faturar OS concluída
GET    /api/financeiro/contas-receber/inadimplente/{clienteId}/ → verificação (chamada interna)
POST   /api/financeiro/pagamentos/              → registar pagamento
GET    /api/financeiro/pagamentos/{id}/         → detalhe
GET    /api/financeiro/mensalidades/configuracao/ → obter valor
PUT    /api/financeiro/mensalidades/configuracao/ → atualizar valor
POST   /api/financeiro/mensalidades/gerar/      → disparar geração manual
```

### conciliacao-service (:8007)

```
POST   /api/conciliacao/importar/          → importar ficheiro (OFX/CSV)
GET    /api/conciliacao/importacoes/       → listar importações
GET    /api/conciliacao/movimentos/        → listar: ?status=
PATCH  /api/conciliacao/movimentos/{id}/ignorar/ → marcar como ignorado
POST   /api/conciliacao/manual/            → conciliar manualmente
GET    /api/conciliacao/pendentes/         → movimentos por conciliar
```

### notification-service (:8008)

```
GET    /api/notificacoes/        → listar notificações
PATCH  /api/notificacoes/{id}/ler/ → marcar como lida
```

---

## Docker Compose — Estrutura Base

### Variáveis de ambiente padrão por serviço

```env
# .env.example (padrão para todos os serviços)
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=service_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db-service-name
DB_PORT=5432
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
ALLOWED_HOSTS=*
```

### Nomenclatura dos containers

```yaml
# docker-compose.yml
services:
  auth-service:
    build: ./backend/auth-service
    container_name: erp_auth
    depends_on: [db-auth, rabbitmq]

  db-auth:
    image: postgres:15
    container_name: erp_db_auth
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  # Padrão repetido para cada microserviço
  # db-usuario, db-cliente, db-servico, db-os, db-financeiro, db-conciliacao, db-notification

  rabbitmq:
    image: rabbitmq:3.12-management
    container_name: erp_rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"  # management UI

  nginx:
    build: ./reverse-proxy
    container_name: erp_nginx
    ports:
      - "80:80"
    depends_on: [auth-service, usuario-service, cliente-service, ...]

  frontend:
    build: ./frontend
    container_name: erp_frontend
```

---

## Padrões de Código Django

### Estrutura base de cada microserviço

```python
# core/settings.py — base igual para todos
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    '<nome_do_app>',  # ex: 'usuarios', 'clientes', 'ordens'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### Padrão de UUID como PK

```python
import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
```

### Padrão de referência externa entre serviços

```python
# Não usar ForeignKey para entidades de outros serviços
# Usar UUIDField simples
class OrdemServico(BaseModel):
    clienteId = models.UUIDField()           # referência externa ao cliente-service
    delegacaoExecucaoId = models.UUIDField() # referência externa ao usuario-service
    usuarioCriacaoId = models.UUIDField()    # referência externa ao auth-service
    # ... demais campos
```

### Padrão de chamada síncrona entre serviços

```python
# services/external.py — padrão para chamadas HTTP entre serviços
import requests
import os

class ClienteServiceClient:
    BASE_URL = os.environ.get('CLIENTE_SERVICE_URL', 'http://cliente-service:8003')

    @staticmethod
    def get_cliente(cliente_id: str, token: str) -> dict:
        response = requests.get(
            f"{ClienteServiceClient.BASE_URL}/api/clientes/{cliente_id}/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def verificar_inadimplente(cliente_id: str, token: str) -> bool:
        response = requests.get(
            f"{ClienteServiceClient.BASE_URL}/api/clientes/{cliente_id}/inadimplente/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        response.raise_for_status()
        return response.json().get('inadimplente', False)
```

---

## requirements.txt Base (igual para todos os serviços)

```txt
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
drf-spectacular==0.27.0
psycopg2-binary==2.9.9
python-decouple==3.8
django-cors-headers==4.3.1
pika==1.3.2
requests==2.31.0
Pillow==10.1.0
gunicorn==21.2.0
```

### Adicionar por serviço específico

```txt
# financeiro-service — scheduler de mensalidades
APScheduler==3.10.4
django-apscheduler==0.6.2

# conciliacao-service — parsing de ficheiros
ofxparse==0.21
pandas==2.1.0
```

---

## CI/CD GitLab — Estrutura do Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - build
  - push
  - deploy-staging
  - deploy-prod

variables:
  REGISTRY: $CI_REGISTRY
  IMAGE_TAG: $CI_COMMIT_SHA

.build_template: &build_template
  stage: build
  script:
    - docker build -t $REGISTRY/$SERVICE_NAME:$IMAGE_TAG ./backend/$SERVICE_NAME

build-auth:
  <<: *build_template
  variables:
    SERVICE_NAME: auth-service

# Repetir para cada serviço

deploy-staging:
  stage: deploy-staging
  environment: staging
  script:
    - docker-compose -f docker-compose.staging.yml up -d

deploy-prod:
  stage: deploy-prod
  environment: production
  when: manual
  script:
    - docker-compose -f docker-compose.prod.yml up -d
```

---

## Features com 2+ Entidades (requisito mínimo: 8)

| # | Feature | Entidades | Serviços encadeados |
|---|---|---|---|
| 1 | Determinação automática de preço na criação de OS | Cliente + ContaReceber + OrdemServico + OrdemServicoServico | cliente-service → financeiro-service |
| 2 | Transição de estado com geração automática de ContaReceber | OrdemServico + OrdemServicoHistorico + ContaReceber | os-service → financeiro-service (evento) |
| 3 | Verificação de inadimplência via mensalidades em aberto | Cliente + ContaReceber | cliente-service → financeiro-service |
| 4 | Geração automática de mensalidades mensais (job) | Cliente + ContaReceber + ConfiguracaoFinanceira | financeiro-service interno |
| 5 | Bloqueio de cancelamento com pagamentos registados | OrdemServico + Pagamento | os-service → financeiro-service |
| 6 | Baixa de duplicata com suporte a pagamento parcial | ContaReceber + Pagamento | financeiro-service interno |
| 7 | Controlo de acesso por perfil e delegação (RBAC) | Usuario + Delegacao + OrdemServico | todos os serviços |
| 8 | Conciliação automática por NIF + valor | MovimentoBancario + Conciliacao + ContaReceber | conciliacao → cliente → financeiro |

---

## Padrão de Commits

- Mensagens em português
- Formato Conventional Commits: `tipo(escopo): descrição`
- Tipos: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`
- Escopo: nome do serviço ou componente (ex: `usuario-service`, `shared`, `auth-service`)
- Granularidade máxima com coerência — cada commit deve representar uma mudança atómica e independente
- Sem referências a ferramentas de geração automática, agentes ou IA
- Subject ≤ 72 chars; corpo opcional apenas quando o "porquê" não é óbvio

---

## Estado Atual do Projeto

### Concluído (análise e design)
- [x] Análise de problemas e requisitos funcionais/não funcionais
- [x] Diagrama de casos de uso (PlantUML)
- [x] Modelo de domínio e ERD (PlantUML)
- [x] Diagramas de sequência SD01-SD05 (PlantUML)
- [x] Solution Design — arquitetura, endpoints, stack, infraestrutura
- [x] Estrutura de pastas definida

### A implementar
- [x] Infraestrutura Docker base (docker-compose, PostgreSQL, RabbitMQ, nginx)
- [x] auth-service — JWT, RBAC, autenticação
- [x] usuario-service — utilizadores, delegações, protecção de rotas
- [ ] cliente-service — clientes, associados, inadimplência
- [ ] servico-service — catálogo, preços por delegação
- [ ] os-service — OS, estados, histórico, eventos
- [ ] financeiro-service — contas a receber, pagamentos, mensalidades, scheduler
- [ ] conciliacao-service — importação, conciliação automática e manual
- [ ] notification-service — consumidor de eventos
- [ ] Frontend React (baseado em design Figma existente)
- [ ] CI/CD GitLab pipeline
- [ ] README completo
- [ ] Postman collection

---

## Distribuição da Equipa

| Membro | Responsabilidade |
|---|---|
| Membro A (sénior) | auth-service, os-service, financeiro-service, infraestrutura Docker, nginx, CI/CD |
| Membro B (médio) | servico-service, conciliacao-service, notification-service, frontend React |
| Membro C (júnior) | usuario-service, cliente-service, testes Postman, README setup, docs/diagrams |

### Ordem de implementação recomendada

```
1. Infraestrutura base (A) — docker-compose, nginx, RabbitMQ funcionando
2. auth-service (A) — JWT + middleware RBAC reutilizável
3. usuario-service (C) — com template base fornecido por A
4. cliente-service (C) — com template base fornecido por A
5. servico-service (B) — necessário antes do os-service
6. os-service (A) — depende de cliente e servico prontos
7. financeiro-service (A) — depende do os-service
8. conciliacao-service (B) — depende do financeiro-service
9. notification-service (B) — consumidor puro, paralelo
10. Frontend (B) — após APIs principais estáveis
11. CI/CD + README + Postman — fase final
```

---

## Padrão para Adicionar um Novo Serviço

### Estrutura de pastas implementada (real)

```
backend/
├── shared/                        ← fonte única da verdade — NÃO duplicar
│   ├── __init__.py
│   ├── rabbitmq.py                ← publish_event(), start_consumer()
│   └── auth_middleware/
│       ├── __init__.py
│       ├── drf_authentication.py  ← JWTStatelessAuthentication (DRF, sem DB — usar em serviços não-auth)
│       ├── middleware.py          ← JWTMiddleware (Django puro, não usar em serviços DRF)
│       ├── decorators.py          ← @require_perfil (views Django puras)
│       └── permissions.py        ← IsOperador…IsAdministrador (hierarquia PERFIL_ORDER), IsMesmaDelegacao
├── auth_service/                  ← único serviço implementado como referência
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── manage.py
│   ├── auth_service/              ← pacote Django (settings, urls, wsgi)
│   └── authentication/            ← app Django
└── <novo_service>/                ← seguir o mesmo padrão do auth_service
```

### docker-compose.override.yml — padrão por serviço

O contexto de build é sempre `./backend/` (não `./backend/<service>/`) para que o
Dockerfile consiga aceder ao `shared/` centralizado.

```yaml
services:
  auth-service:
    build:
      context: ./backend
      dockerfile: auth_service/Dockerfile

  usuario-service:                   # exemplo de novo serviço
    build:
      context: ./backend
      dockerfile: usuario_service/Dockerfile
```

### Dockerfile — padrão por serviço

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd curl && rm -rf /var/lib/apt/lists/*

# Caminho relativo ao contexto de build (./backend/)
COPY <nome_service>/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# shared/ copiado de backend/shared/ — sem duplicação no repositório
COPY shared/ ./shared/

# Código do serviço
COPY <nome_service>/ .

COPY <nome_service>/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE <porta>

ENTRYPOINT ["/entrypoint.sh"]
```

### shared/ — regra de utilização

- `backend/shared/` é a **única cópia** no repositório — nunca duplicar para dentro de um serviço
- **auth_middleware/**: usado por todos os serviços excepto o auth-service (que emite tokens, não valida)
- **rabbitmq.py**: usado por todos os serviços que publicam ou consomem eventos

```python
# Autenticação DRF — todos os serviços excepto auth-service:
# Adicionar ao REST_FRAMEWORK em settings.py:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'shared.auth_middleware.drf_authentication.JWTStatelessAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    ...
}
# JWTStatelessAuthentication valida JWT sem DB lookup.
# Define request.user (_JWTUser) e request.auth (payload dict) no sistema DRF.
# NÃO adicionar JWTMiddleware ao MIDDLEWARE — redundante e na camada errada para DRF.

# Proteger uma view por perfil (class-based view):
from shared.auth_middleware.permissions import IsOperador, IsAdministrador

class MinhaView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOperador()]
        return [IsAdministrador()]

    def get(self, request):
        usuario_id = request.auth.get('usuarioId')
        delegacao_id = request.auth.get('delegacaoId')
        perfil = request.auth.get('perfil')
        ...

# Publicar um evento RabbitMQ:
from shared.rabbitmq import publish_event

publish_event('usuario.criado', {'usuarioId': str(id), 'email': email, 'perfil': perfil})

# Consumir eventos:
from shared.rabbitmq import start_consumer

start_consumer('nome_da_fila', ['routing.key.*'], callback_fn)
```

### VS Code — extraPaths (já configurado em .vscode/settings.json)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.analysis.extraPaths": [
    "${workspaceFolder}/backend/auth_service",
    "${workspaceFolder}/backend"
  ]
}
```

Quando adicionares um novo serviço, acrescentar o seu path aos `extraPaths`:
```json
"${workspaceFolder}/backend/usuario_service"
```

---

## Notas Importantes para Implementação

1. **Nunca usar ForeignKey entre serviços** — referências externas são sempre UUIDField simples
2. **Cada serviço tem o seu PostgreSQL** — nunca aceder à DB de outro serviço diretamente
3. **JWT validado localmente via `JWTStatelessAuthentication`** — sem chamada ao auth-service a cada request; `JWTMiddleware` existe no shared mas destina-se a views Django puras (não DRF)
4. **Ficheiros .env nunca versionados** — apenas .env.example no git
5. **RabbitMQ com exchange do tipo topic** — permite subscrição por padrão de routing key
6. **Todos os IDs são UUID** — nunca integer auto-increment
7. **camelCase nos campos dos models** — conforme definido no ERD aprovado
8. **Histórico de OS obrigatório** — qualquer transição de estado grava OrdemServicoHistorico
9. **Log de auditoria via eventos** — notification-service regista todos os eventos RabbitMQ
10. **Scheduler de mensalidades** — corre no financeiro-service no dia 1 de cada mês
11. **shared/ nunca duplicado** — contexto de build é sempre `./backend/`; Dockerfile copia `shared/` do central
12. **auth_service como referência** — ao criar um novo serviço, seguir a estrutura de `backend/auth_service/` como template
