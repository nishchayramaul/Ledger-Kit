"""create journal_entries

Revision ID: 4a360df5462e
Revises: 0001
Create Date: 2026-10-22 12:21:38.615246
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4a360df5462e"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("external_ref", sa.String(128), nullable=True),
        sa.Column(
            "effective_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    op.create_table(
        "postings",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("postings")
    op.drop_table("journal_entries")
