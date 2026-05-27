# ERP Associação Agrícola

Sistema ERP Web centralizado para associação agrícola com 9 delegações regionais.

## Quick Start — Executar Localmente

### 1. Preparar ambiente

```bash
cp .env.example .env
```

O `.env` na raiz é partilhado por todos os serviços. As únicas variáveis que diferem por serviço (`DB_HOST`, `DB_NAME`) são injetadas diretamente no `docker-compose.yml`.
O `notification-service` também lê `SMTP_HOST`, `SMTP_PORT` e `EMAIL_FROM` a partir desse `.env`, com os defaults de desenvolvimento `mailhog`, `1025` e `noreply@erp-associacao.pt`.

### 2. Subir containers

```bash
docker-compose up -d
```

Aguarde ~30s. Verifique status:
```bash
docker-compose ps
```

Todos devem estar `Up` com health `healthy`.

### 3. Testar auth-service

**Health check:**
```bash
curl http://localhost:8001/api/auth/health/
```

**Swagger docs:**
```
http://localhost:8001/api/docs/
```

### 4. Testar usuario-service

**Health check:**
```bash
curl http://localhost:8002/api/usuarios/health/
```

**Swagger docs:**
```
http://localhost:8002/api/docs/
```

### 5. Testar notification-service

**Health check:**
```bash
curl http://localhost:8009/api/notificacoes/health/
```

**Swagger docs:**
```
http://localhost:8009/api/docs/
```

**Login de teste:**
```bash
# Primeiro criar uma credencial
docker exec ldsgrupo1_auth python manage.py shell
```

```python
from authentication.models import Credencial
from django.contrib.auth.hashers import make_password
from uuid import uuid4

Credencial.objects.create(
    usuarioId=uuid4(),
    delegacaoId=uuid4(),
    email='teste@example.com',
    passwordHash=make_password('senha123'),
    perfil='ADMINISTRADOR'
)
```

```bash
# Depois fazer login
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@example.com","password":"senha123"}'
```

## Arquitetura

```
backend/
├── auth_service/              (porta 8001 - JWT, autenticação)
│   ├── Dockerfile             (específico para auth)
│   ├── requirements.txt
│   └── authentication/
├── usuario_service/           (porta 8002 - utilizadores, delegações)
│   └── (usa backend/docker/Dockerfile)
├── docker/                    (templates COMPARTILHADOS para novos serviços)
│   ├── Dockerfile             (copiar para novos serviços)
│   ├── requirements.txt        (dependências base)
│   └── entrypoint.sh
└── ...

frontend/                       (porta 3000 - React)
reverse-proxy/                  (nginx na porta 80)

docker-compose.yml              (orquestra tudo - infra + serviços)
```

## Estrutura de Pasta

- **backend/**: Serviços Django (microserviços)
- **frontend/**: React UI
- **docs/**: Documentação
- **reverse-proxy/**: Nginx config
- **postman/**: Coleções Postman
- **CLAUDE.md**: Documentação completa (leia isto!)

## Ficheiros Importantes

| Ficheiro | Propósito |
|----------|-----------|
| `docker-compose.yml` | Orquestra auth, usuario, rabbitmq, nginx, postgresql |
| `setup.sh` | Cria ficheiros `.env` do ambiente |
| `.env.example` | Template das variáveis partilhadas, incluindo SMTP do notification-service |
| `CLAUDE.md` | Especificação completa (arquitetura, endpoints, modelos, regras de negócio) |

## Status de Implementação

| Serviço | Status |
|---------|--------|
| auth-service | ✅ Completo (login, refresh, logout, RBAC) |
| usuario-service | ⏳ Estrutura base |
| cliente-service | ⏳ Não iniciado |
| servico-service | ⏳ Não iniciado |
| os-service | ⏳ Não iniciado |
| financeiro-service | ⏳ Não iniciado |
| conciliacao-service | ⏳ Não iniciado |
| notification-service | ⏳ Não iniciado |
| frontend | ⏳ Não iniciado |

## Logs e Debugging

```bash
# Ver logs do auth-service
docker logs -f ldsgrupo1_auth

# Ver logs do usuario-service
docker logs -f usuario-service

# Entrar no shell Django
docker exec ldsgrupo1_auth python manage.py shell

# Parar tudo
docker-compose down
```

## CI/CD — Pipeline GitLab

O pipeline está definido em `.gitlab-ci.yml` e tem 5 stages: `build → push → deploy-develop → deploy-staging → deploy-production`.

### Variáveis obrigatórias no GitLab

Configurar em **Settings → CI/CD → Variables** antes de executar o pipeline:

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `SSH_PRIVATE_KEY` | Variable (Protected) | Chave privada SSH para acesso à VM |
| `SSH_HOST` | Variable | Endereço IP da VM de deploy |
| `SSH_USER` | Variable | Utilizador SSH (ex: `ubuntu`) |
| `DEVELOP_ENV` | File | Conteúdo do `.env` para o ambiente develop |
| `STAGING_ENV` | File | Conteúdo do `.env` para o ambiente staging |
| `PRODUCTION_ENV` | File | Conteúdo do `.env` para o ambiente de produção |

> As variáveis `CI_REGISTRY`, `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD` e `CI_REGISTRY_IMAGE` são preenchidas automaticamente pelo GitLab.

### Branches e ambientes

| Branch | Deploy automático | Ambiente |
|--------|-------------------|----------|
| `develop` | Sim | `/opt/erp/develop` na VM |
| `staging` | Sim | `/opt/erp/staging` na VM |
| `main` | Manual (aprovação) | `/opt/erp/production` na VM |

---

## Git Workflow

Cada mudança = **um commit com mensagem clara em português**. Exemplo:

```bash
git commit -m "feat(auth): implementar endpoint de login

Adiciona POST /api/auth/login/ com validação de credenciais
e geração de JWT com claims personalizados."
```

Veja os commits recentes com:
```bash
git log --oneline | head -20
```

## Contatos & Distribuição

Veja a seção "Distribuição da Equipa" em CLAUDE.md para saber quem é responsável por cada serviço.
