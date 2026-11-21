"""create tenants and accounts

Revision ID: f352ff5b9567
Revises:
Create Date: 2026-10-21 18:50:08.043280
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


NORMAL_BALANCE_EXPRESSION = "CASE WHEN type IN ('asset', 'expense') THEN 'debit' ELSE 'credit' END"


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("name", name="uq_tenants_name"),
        sa.CheckConstraint("status IN ('active', 'suspended')", name="ck_tenants_status"),
    )
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("currency", sa.CHAR(3), nullable=False),
        sa.Column(
            "normal_balance",
            sa.Text(),
            sa.Computed(NORMAL_BALANCE_EXPRESSION, persisted=True),
            nullable=False,
        ),
        sa.Column("overdraft_policy", sa.Text(), nullable=False, server_default="disallow"),
        sa.Column("overdraft_limit_minor", sa.BigInteger(), nullable=True),
        sa.Column("external_ref", sa.String(128), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("tenant_id", "code", name="uq_accounts_tenant_code"),
        sa.UniqueConstraint("tenant_id", "external_ref", name="uq_accounts_tenant_external_ref"),
        sa.CheckConstraint("code ~ '^[A-Z][A-Z0-9_]*$'", name="ck_accounts_code_format"),
        sa.CheckConstraint(
            "type IN ('asset', 'liability', 'equity', 'income', 'expense')",
            name="ck_accounts_type",
        ),
        sa.CheckConstraint("currency ~ '^[A-Z]{3}$'", name="ck_accounts_currency_format"),
        sa.CheckConstraint(
            "overdraft_policy IN ('disallow', 'allow', 'limit')",
            name="ck_accounts_overdraft_policy",
        ),
        sa.CheckConstraint(
            "overdraft_limit_minor > 0", name="ck_accounts_overdraft_limit_positive"
        ),
        sa.CheckConstraint(
            "(overdraft_policy = 'limit') = (overdraft_limit_minor IS NOT NULL)",
            name="ck_accounts_overdraft_limit_matches_policy",
        ),
    )
    # Alembic has no command for triggers, so this part is plain SQL
    op.execute(
        """
        CREATE FUNCTION accounts_reject_immutable_changes() RETURNS trigger AS $$
        BEGIN
            IF NEW.type IS DISTINCT FROM OLD.type
            OR NEW.currency IS DISTINCT FROM OLD.currency
            OR NEW.code IS DISTINCT FROM OLD.code
            OR NEW.tenant_id IS DISTINCT FROM OLD.tenant_id THEN
                RAISE EXCEPTION 'account type, currency, code and tenant cannot change'
                    USING ERRCODE = 'check_violation';
            END IF;
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_accounts_immutable
            BEFORE UPDATE ON accounts
            FOR EACH ROW EXECUTE FUNCTION accounts_reject_immutable_changes()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER trg_accounts_immutable ON accounts")
    op.execute("DROP FUNCTION accounts_reject_immutable_changes()")
    op.drop_table("accounts")
    op.drop_table("tenants")
