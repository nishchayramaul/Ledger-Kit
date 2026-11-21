from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.account import Account
from app.models.tenant import Tenant

DEMO_TENANT_NAME = "PayLite (demo)"
DEMO_CURRENCY = "INR"
DEMO_ACCOUNTS = [
    {"code": "BANK_HDFC", "name": "PayLite HDFC bank account", "type": "asset"},
    {"code": "W_RAHUL", "name": "Rahul's wallet", "type": "liability"},
    {"code": "W_ASHA", "name": "Asha's wallet", "type": "liability"},
    {"code": "FEE_INCOME", "name": "Fee income", "type": "income"},
]


# returns the demo tenant's id, creating the tenant on the first run
def get_or_create_demo_tenant(db: Session) -> UUID:
    db.execute(
        insert(Tenant)
        .values(name=DEMO_TENANT_NAME)
        .on_conflict_do_nothing(constraint="uq_tenants_name")
    )
    return db.scalars(select(Tenant.id).where(Tenant.name == DEMO_TENANT_NAME)).one()


# adds the demo accounts that don't exist yet and returns how many were added
def create_demo_accounts(db: Session, tenant_id: UUID) -> int:
    new_accounts = [
        {**account, "tenant_id": tenant_id, "currency": DEMO_CURRENCY} for account in DEMO_ACCOUNTS
    ]
    inserted = db.execute(
        insert(Account)
        .values(new_accounts)
        .on_conflict_do_nothing(constraint="uq_accounts_tenant_code")
        .returning(Account.id)
    )
    return len(inserted.all())


def main() -> None:
    with SessionLocal() as db:
        tenant_id = get_or_create_demo_tenant(db)
        added = create_demo_accounts(db, tenant_id)
        db.commit()
    print(f"Demo tenant id: {tenant_id}")
    print(f"Added {added} demo accounts ({len(DEMO_ACCOUNTS) - added} already existed)")
    print(f"Put APP_DEFAULT_TENANT_ID={tenant_id} in .env and restart the API")


if __name__ == "__main__":
    main()
