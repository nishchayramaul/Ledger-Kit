from fastapi import FastAPI

from app.api.error_handler import register_error_handlers
from app.api.routes.accounts import router as accounts_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.middleware import add_middlewares


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.app_log_level)
    app: FastAPI = FastAPI(title=settings.app_name)
    add_middlewares(app)
    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(accounts_router)
    return app


app = create_app()
