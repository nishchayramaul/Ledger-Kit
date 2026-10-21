from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.app_log_level)

from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.middleware.middleware import generate_request_id

def create_app() -> FastAPI:
    app: FastAPI = FastAPI(title=settings.app_name)
    app.middleware("http")(generate_request_id)
    app.include_router(health_router)
    return app


app = create_app()
