# ERP Associação Agrícola

Sistema ERP Web centralizado para associação agrícola com 9 delegações regionais.

## Quick Start — Executar Localmente

### 1. Preparar ambiente

```bash
# No Windows PowerShell ou bash
bash setup.sh
```

Isto cria os ficheiros `.env` necessários a partir dos templates.

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

**Login de teste:**
```bash
# Primeiro criar uma credencial
docker exec erp_auth python manage.py shell
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
| `.env.example` | Template das variáveis de auth-service |
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
docker logs -f erp_auth

# Ver logs do usuario-service
docker logs -f usuario-service

# Entrar no shell Django
docker exec erp_auth python manage.py shell

# Parar tudo
docker-compose down
```

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
