.PHONY: dev down logs infra-up migrate seed test lint build verify

dev:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs --follow

infra-up:
	docker compose up --detach postgres redis minio minio-init

migrate:
	docker compose run --rm backend uv run alembic upgrade head

seed:
	docker compose run --rm backend env PYTHONPATH=src uv run python -m file2formai.cli.seed

test:
	cd backend && uv run pytest -m "not integration"
	corepack pnpm --filter @file2formai/web test

lint:
	cd backend && uv run ruff check .
	cd backend && uv run ruff format --check .
	corepack pnpm --filter @file2formai/web lint
	corepack pnpm --filter @file2formai/web typecheck

build:
	corepack pnpm --filter @file2formai/web build

verify: test lint build
	docker compose config --quiet
