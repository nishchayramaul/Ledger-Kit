import os

PLACEHOLDER_DB_URL = "postgresql+psycopg://ledgerkit:ledgerkit@localhost:5432/ledgerkit"
TEST_TENANT_ID = "6f1c2a3e-8b4d-4c5e-9f60-7a8b9c0d1e2f"

test_database_url = os.environ.get("TEST_DATABASE_URL") or PLACEHOLDER_DB_URL

os.environ["APP_ENV"] = "test"
os.environ["APP_DB_URL"] = test_database_url
os.environ["APP_DB_MIGRATION_URL"] = test_database_url
os.environ["APP_DEFAULT_TENANT_ID"] = TEST_TENANT_ID
