from contextvars import ContextVar
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

REQUEST_ID_HEADER = "X-Request-Id"

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


async def generate_request_id(request: Request, call_next: RequestResponseEndpoint) -> Response:
    request_id = request.headers.get(REQUEST_ID_HEADER) or "req_" + uuid4().hex
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = request_id
    return response
