# Task Manager — To-Do List

Gerenciador de tarefas com categorias, compartilhamento entre usuários,
autenticação JWT, filtros, paginação e API documentada (OpenAPI/Swagger).

> Teste prático. Stack: **Django REST Framework + React (TypeScript) + PostgreSQL +
> Redis + Celery + Docker**. CI/CD via GitHub Actions. Deploy AWS via Terraform.

---

## Índice
- [Arquitetura](#arquitetura)
- [Decisões de design](#decisões-de-design)
- [Segurança (OWASP)](#segurança-owasp)
- [Como rodar](#como-rodar)
- [Testes](#testes)
- [API](#api)

---

## Arquitetura

Monorepo com serviços isolados, orquestrados por Docker Compose:

```
                     ┌─────────────┐
   Browser  ───────▶ │    Nginx    │  (reverse proxy, TLS, static)
                     └──────┬──────┘
                 ┌──────────┴──────────┐
         ┌───────▼───────┐     ┌───────▼────────┐
         │ React (Vite)  │     │  Django + DRF  │ (Gunicorn)
         │  SPA / TS     │     │  API /api/v1   │
         └───────────────┘     └───┬────────┬───┘
                                   │        │
                        ┌──────────▼─┐   ┌──▼──────┐
                        │ PostgreSQL │   │  Redis  │◀── cache + throttle + broker
                        └────────────┘   └────┬────┘
                                              │
                                        ┌─────▼─────┐
                                        │  Celery   │ (email async ao compartilhar)
                                        └───────────┘
```

### Backend em camadas (SOLID / SRP)

```
apps/<domínio>/
  models.py        # persistência (ORM)
  serializers.py   # validação + (de)serialização I/O
  services.py      # regra de negócio — única fonte da lógica
  permissions.py   # autorização object-level (BOLA)
  views.py         # HTTP: orquestra serializer + service, sem regra de negócio
  filters.py       # filtros de query
```

A **service layer** existe para que a regra de negócio não fique espalhada nas
views. Views ficam finas (HTTP in/out), serializers só validam, services detêm
a lógica. Facilita teste unitário (testa service sem HTTP) e troca de interface.

---

## Decisões de design

| Decisão | Porquê |
|---------|--------|
| Service layer separada das views | SRP: regra de negócio testável e reutilizável (Celery e views chamam o mesmo service) |
| PostgreSQL, não SQLite | Paridade dev/prod; suporta índices/constraints reais |
| JWT (access curto + refresh) | Stateless, escala horizontalmente sem sessão sticky |
| Redis multiuso | Cache, rate-limit e broker Celery num só serviço |
| Celery para email | Compartilhar tarefa não bloqueia a request HTTP |
| Settings split base/dev/prod | 12-factor; segredos por ambiente, sem `if DEBUG` espalhado |
| drf-spectacular | Swagger gerado do código — doc nunca desatualiza |
| API versionada `/api/v1` | Evolução sem quebrar clientes |

---

## Segurança (OWASP)

Mapeamento explícito para OWASP Top 10 (Web + API):

| Controle | OWASP | Onde |
|----------|-------|------|
| Permissão object-level por tarefa | API1 BOLA | `apps/tasks/permissions.py` |
| JWT + rotação/blacklist de refresh | API2 Broken Auth | `config/settings/base.py` (SIMPLE_JWT) |
| Throttling por usuário/anon | API4 Resource Consumption | DRF throttle + Redis |
| Validação de entrada (serializers) + ORM | A03 Injection | serializers + Django ORM |
| Segredos em `.env`, nunca no repo | A05 Misconfiguration | `.env.example` versionado, `.env` ignorado |
| Security headers + HSTS | A05 | `SecurityMiddleware` em `prod.py` |
| CORS por whitelist | A05 | `django-cors-headers` |
| Lockout de brute-force | A07 Auth Failures | `django-axes` |
| Hash Argon2 + validators de senha | A02/A07 | `PASSWORD_HASHERS`, `AUTH_PASSWORD_VALIDATORS` |
| Log estruturado / auditoria | A09 Logging | `LOGGING` config |
| Scan de dependências no CI | A06 Vulnerable Components | `pip-audit` + `bandit` no pipeline |

---

## Como rodar

Pré-requisitos: Docker + Docker Compose.

```bash
cp .env.example .env          # ajuste se quiser
make build
make migrate
make up                       # http://localhost (Nginx) | API em /api/v1
make superuser                # opcional, acessa /admin
```

`make help` lista todos os comandos.

---

## Testes

```bash
make test     # pytest + coverage (backend)
make e2e      # Selenium (frontend)
make lint     # black, isort, flake8, mypy
```

---

## API

Docs interativas (self-documenting external API — requisito d):
- Swagger UI: `http://localhost/api/v1/docs/`
- OpenAPI JSON: `http://localhost/api/v1/schema/`

Todas as rotas sob `/api/v1/`. JWT no header `Authorization: Bearer <access>`.

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/auth/register/` | Criar conta | — |
| POST | `/auth/login/` | Obter par JWT (access+refresh) | — |
| POST | `/auth/refresh/` | Renovar access token | — |
| GET | `/auth/me/` | Usuário atual | JWT |
| GET/POST | `/tasks/` | Listar (filtro+paginação) / criar | JWT |
| GET/PATCH/DELETE | `/tasks/{id}/` | Detalhe / editar / remover | JWT + object-level |
| PATCH | `/tasks/{id}/status/` | Marcar concluída / não | JWT |
| POST | `/tasks/{id}/share/` | Compartilhar por e-mail | dono |
| DELETE | `/tasks/{id}/share/{user_id}/` | Revogar compartilhamento | dono |
| GET/POST | `/categories/` | Listar / criar categorias | JWT |

**Filtros de tarefa:** `?status=done` · `?category=3` · `?search=texto` ·
`?ordering=-created_at` · `?due_before=<iso>` · `?page=2&page_size=50`

### Verificação

Stack validada de ponta a ponta via Nginx: registro → login JWT → criar tarefa
→ listar paginado → compartilhar → e-mail assíncrono entregue pelo Celery.
Backend: 20 testes pytest, 92% cobertura. Front: typecheck + build + Selenium E2E.

### Deploy

Ver [infra/terraform/README.md](infra/terraform/README.md). Stack de produção:
`docker compose -f docker-compose.prod.yml up --build -d` (Gunicorn + Nginx +
SPA compilada).
