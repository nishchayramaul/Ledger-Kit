ALEMBIC = uv run alembic

.PHONY: up run seed lint typecheck test check db-up db-down db-reset migrate migrate-status migrate-history migrate-preview migrate-rollback migration migration-auto

up: migrate run

run:
	uv run python -m app

seed:
	uv run python -m app.scripts.seed_demo_data

lint:
	uv run ruff check .
	uv run python -m app.scripts.check_no_float_in_money

typecheck:
	uv run mypy app tests

test:
	uv run pytest

check: lint typecheck test

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

db-reset:
	docker compose down -v

migrate:
	$(ALEMBIC) upgrade head

migrate-status:
	$(ALEMBIC) current --verbose

migrate-history:
	$(ALEMBIC) history --verbose

migrate-preview:
	$(ALEMBIC) upgrade head --sql

migrate-rollback:
	$(ALEMBIC) downgrade -1

migration:
	$(ALEMBIC) revision -m "$(m)"

migration-auto:
	$(ALEMBIC) revision --autogenerate -m "$(m)"
