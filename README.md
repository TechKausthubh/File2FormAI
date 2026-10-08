# File2FormAI

File2FormAI is a generic, configurable, multi-tenant AI troubleshooting platform. A technician will select equipment, describe a problem, and receive guidance grounded in approved technical documentation with traceable source citations.

Army maintenance is the first use case, but the platform core is domain-neutral so it can also support fleet maintenance, manufacturing, automotive, logistics, industrial equipment, and defense contractors.

## Repository status

This repository contains the initial development skeleton and multi-tenant domain foundation:

- a React/Vite application shell with navigation and API health status;
- a FastAPI service exposing `/health` and database-backed `/ready` endpoints;
- organization, settings, membership, and equipment APIs with explicit tenant context;
- an explicit local-development identity adapter and deterministic two-organization seed;
- an Alembic migration that enables pgvector; and
- a local Docker Compose environment with PostgreSQL/pgvector, Redis, MinIO, the API, and the web app.

Production authentication, document ingestion, retrieval/RAG, agents, MCP tools, voice, and feature UI are intentionally not implemented. The local identity adapter is development-only and is not suitable for an external pilot.

## Prerequisites

The primary workflow requires:

- Docker Desktop with Docker Compose v2; and
- enough free Docker storage for the application images and persistent volumes.

For running checks or services directly on the host, also install:

- Node.js 20.19.0 or newer in the Node 20 line, with Corepack;
- `uv`; and
- Python 3.12, which `uv` can manage automatically.

The repository pins pnpm 10.34.6 in `package.json`. Frontend packages are locked in `pnpm-lock.yaml`; Python packages are locked in `backend/uv.lock`. Do not update either lockfile without running the corresponding checks.

## Primary startup workflow

From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

The first build compiles the final open-source MinIO security release from its pinned upstream source tag because a stable public upstream image is no longer available. Later starts reuse the built image and named volumes.

The Compose configuration waits for PostgreSQL, runs `alembic upgrade head`, starts the API, creates the MinIO bucket idempotently, and then starts the web application.

Local URLs:

- Web application: <http://localhost:5173>
- API health: <http://localhost:8000/health>
- API readiness: <http://localhost:8000/ready>
- FastAPI documentation: <http://localhost:8000/docs>
- MinIO S3 endpoint: <http://localhost:9000>
- MinIO console: <http://localhost:9001>
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

All development ports bind only to `127.0.0.1`. Stop the stack without deleting data:

```bash
docker compose down
```

Named volumes preserve PostgreSQL, Redis, MinIO, and container-side frontend dependency data.

## Environment configuration

The root `.env` is read by Docker Compose and contains local infrastructure credentials. Begin with `.env.example` and change the development credentials if needed.

`backend/.env` is backend-only and may contain secrets:

```bash
cp backend/.env.example backend/.env
```

`apps/web/.env` is compiled into browser code and must contain public values only:

```bash
cp apps/web/.env.example apps/web/.env
```

Only `VITE_API_BASE_URL` is currently supported in browser configuration. Never place database credentials, object-storage credentials, provider tokens, or API keys in a `VITE_*` variable.

Local `.env` files are ignored; `.env.example` files remain tracked.

### Development identity

The Compose environment explicitly enables a deterministic development user:

```text
20000000-0000-4000-8000-000000000001
```

Tenant API requests must select an organization with `X-Development-Organization-ID`. The backend verifies that the configured development user has a membership in the selected organization before constructing the trusted request context. The adapter fails application configuration if it is enabled when `F2F_ENVIRONMENT` is `test` or `production`.

## Host development workflow

Start infrastructure:

```bash
docker compose up --detach postgres redis minio minio-init
```

Install and run the backend in one terminal:

```bash
cp backend/.env.example backend/.env
cd backend
uv sync --frozen --python 3.12
uv run alembic upgrade head
uv run uvicorn file2formai.main:app --app-dir src --reload --host 127.0.0.1 --port 8000
```

Install and run the frontend from the repository root in another terminal:

```bash
corepack enable
corepack pnpm install --frozen-lockfile
cp apps/web/.env.example apps/web/.env
corepack pnpm web:dev
```

## Migrations

Compose applies existing migrations during normal backend startup. Apply them explicitly with:

```bash
docker compose run --rm backend uv run alembic upgrade head
```

For a host-run backend:

```bash
cd backend
uv run alembic upgrade head
```

Verify the migration and pgvector extension against the real local PostgreSQL container:

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT extversion FROM pg_extension WHERE extname = '\''vector'\'';"'
```

All future database changes require a new Alembic migration.

## Development seed

Run the idempotent seed explicitly; it never runs automatically:

```bash
make seed
```

Equivalent Compose command:

```bash
docker compose run --rm backend env PYTHONPATH=src uv run python -m file2formai.cli.seed
```

The seed creates two isolated organizations with distinct settings and equipment. The development administrator belongs to both organizations; each organization also has its own technician.

| Organization | ID |
| --- | --- |
| Northstar Field Services | `10000000-0000-4000-8000-000000000001` |
| Harborline Manufacturing | `10000000-0000-4000-8000-000000000002` |

The CLI refuses to run unless `F2F_ENVIRONMENT=development`.

## Domain API examples

Set a development organization header and read the active organization:

```bash
export F2F_DEMO_ORGANIZATION_ID=10000000-0000-4000-8000-000000000001
curl -H "X-Development-Organization-ID: $F2F_DEMO_ORGANIZATION_ID" \
  http://127.0.0.1:8000/api/v1/organization
curl -H "X-Development-Organization-ID: $F2F_DEMO_ORGANIZATION_ID" \
  http://127.0.0.1:8000/api/v1/organization/settings
curl -H "X-Development-Organization-ID: $F2F_DEMO_ORGANIZATION_ID" \
  http://127.0.0.1:8000/api/v1/equipment-models
```

Create an equipment model as the seeded development administrator:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-Development-Organization-ID: $F2F_DEMO_ORGANIZATION_ID" \
  -d '{"manufacturer":"Summit Equipment","model_name":"HX-7","description":"Hydraulic test unit","metadata":{"category":"test-equipment"}}' \
  http://127.0.0.1:8000/api/v1/equipment-models
```

Available tenant endpoints are:

- `GET/PATCH /api/v1/organization`
- `GET/PATCH /api/v1/organization/settings`
- `GET /api/v1/members`
- `GET/POST /api/v1/equipment-models`
- `GET/PATCH/DELETE /api/v1/equipment-models/{id}`
- `GET/POST /api/v1/equipment-instances`
- `GET/PATCH/DELETE /api/v1/equipment-instances/{id}`

All organization members may read equipment. For this initial version, organization updates, member listing, and equipment mutations require `org_admin`. Deleting an equipment model that still has instances returns HTTP 409; delete or reassign its instances first.

## Verification commands

After installing host dependencies, run the complete infrastructure-independent suite from the repository root:

```bash
make verify
```

Equivalent commands are:

```bash
cd backend && uv run ruff check .
cd backend && uv run ruff format --check .
cd backend && uv run pytest -m "not integration"
corepack pnpm --filter @file2formai/web test
corepack pnpm --filter @file2formai/web lint
corepack pnpm --filter @file2formai/web typecheck
corepack pnpm --filter @file2formai/web build
docker compose config --quiet
```

### PostgreSQL integration tests

Integration tests use only a database whose name ends in `_test`. Create and migrate the isolated database without touching development data:

```bash
docker compose exec postgres sh -c 'if ! psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='\''file2formai_test'\''" | grep -q 1; then createdb -U "$POSTGRES_USER" file2formai_test; fi'
docker compose run --rm --no-deps \
  -e F2F_DATABASE_URL=postgresql+asyncpg://file2formai:file2formai_dev@postgres:5432/file2formai_test \
  -e F2F_ENVIRONMENT=test \
  -e F2F_DEVELOPMENT_IDENTITY_ENABLED=false \
  backend uv run alembic upgrade head
docker compose run --rm --no-deps \
  -e F2F_TEST_DATABASE_URL=postgresql+asyncpg://file2formai:file2formai_dev@postgres:5432/file2formai_test \
  -e F2F_ENVIRONMENT=test \
  -e F2F_DEVELOPMENT_IDENTITY_ENABLED=false \
  backend uv run pytest -m integration
```

Infrastructure-independent backend tests explicitly exclude that marker:

```bash
cd backend && uv run pytest -m "not integration"
```

With the stack running, verify live behavior:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/ready
docker compose ps
```

`/health` returns `200 {"status":"ok"}` when the API process is alive. `/ready` returns `200 {"status":"ok"}` only when PostgreSQL answers `SELECT 1`.

Verify the safe unavailable path without stopping the API:

```bash
docker compose stop postgres
curl -i http://127.0.0.1:8000/ready
docker compose start postgres
```

The middle command must return `503 {"status":"unavailable"}` without credentials or raw driver details. Wait for PostgreSQL to become healthy, then `/ready` should return 200 again.

The MinIO bucket initializer is idempotent and can be rerun with:

```bash
docker compose run --rm minio-init
```

## Root commands

| Command | Purpose |
| --- | --- |
| `make dev` | Build and start the complete Compose development stack |
| `make down` | Stop the stack while preserving named volumes |
| `make logs` | Follow Compose logs |
| `make infra-up` | Start PostgreSQL, Redis, MinIO, and bucket initialization |
| `make migrate` | Apply Alembic migrations through Compose |
| `make seed` | Idempotently create the two local demo tenants |
| `make test` | Run backend and frontend unit tests |
| `make lint` | Run Ruff, ESLint, and TypeScript checks |
| `make build` | Produce the frontend production build |
| `make verify` | Run tests, lint/type checks, build, and Compose validation |

## Repository structure

```text
apps/web/                          React/Vite/TypeScript SPA
  src/app/                         router and application providers
  src/components/layout/           sidebar/header shell
  src/components/ui/               shadcn/ui-compatible primitives
  src/features/                    feature-owned pages and queries
  src/lib/                         public environment and API utilities
backend/                           Python 3.12 FastAPI service
  src/file2formai/api/             thin HTTP routes and dependencies
  src/file2formai/core/            typed settings, database, and logging
  src/file2formai/identity/        users, memberships, and request context
  src/file2formai/organizations/   tenant root and configurable settings
  src/file2formai/equipment/       tenant-scoped models and instances
  src/file2formai/services/        application services
  migrations/                      Alembic environment and revisions
  tests/                           infrastructure-independent tests
infra/minio/                       reproducible MinIO source-build image
docs/                              architecture, data model, and ADRs
docker-compose.yml                 complete local development stack
Makefile                           root development commands
```

## Architecture documentation

- [Architecture](docs/architecture.md)
- [Data model](docs/data-model.md)
- [ADR 0001](docs/adr/0001-initial-architecture.md)
- [Contributor guidance](AGENTS.md)
