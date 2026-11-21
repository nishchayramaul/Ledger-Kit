from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.error import TenantNotConfigured


# returns the tenant for this request; one demo tenant from .env until API keys arrive in LK-18
def get_current_tenant_id(settings: Annotated[Settings, Depends(get_settings)]) -> UUID:
    if settings.app_default_tenant_id is None:
        raise TenantNotConfigured(
            "Set APP_DEFAULT_TENANT_ID in .env; `make seed` prints the demo tenant id"
        )
    return settings.app_default_tenant_id
