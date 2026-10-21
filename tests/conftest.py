import os

os.environ["APP_ENV"] = "test"
os.environ["APP_DB_URL"] = "postgresql+psycopg://ledgerkit:ledgerkit@localhost:5432/ledgerkit"
