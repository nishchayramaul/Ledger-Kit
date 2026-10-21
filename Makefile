ALEMBIC = uv run alembic

.PHONY: up run db-up db-down db-reset migrate migrate-status migrate-history migrate-preview migrate-rollback migration migration-auto

up: migrate run

run:
	uv run python -m app

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
