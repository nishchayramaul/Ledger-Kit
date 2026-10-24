from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

REQUEST_ID_HEADER = "X-Request-Id"


# gives every request an id, reusing the client's id only when it is a valid UUID
def add_middlewares(app: FastAPI) -> None:
    app.add_middleware(CorrelationIdMiddleware, header_name=REQUEST_ID_HEADER)
