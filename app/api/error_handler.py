import logging
from typing import Any

from asgi_correlation_id import correlation_id
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_problem.handler import add_exception_handler, new_exception_handler
from starlette.responses import Response

from app.core.error import UnexpectedError
from app.middleware.middleware import REQUEST_ID_HEADER

ERROR_TYPE_URL = "https://ledgerkit.dev/errors/{type}"


# puts the request id in every error body; 500s skip the middleware, so they also get the header
def add_request_id(
    content: dict[str, Any], request: Request, response: Response
) -> tuple[dict[str, Any], Response]:
    request_id = correlation_id.get() or "-"
    content = {**content, "request_id": request_id}
    headers = {key: value for key, value in response.headers.items() if key != "content-length"}
    if response.status_code >= 500:
        headers[REQUEST_ID_HEADER] = request_id
    return content, JSONResponse(content, status_code=response.status_code, headers=headers)


def register_error_handlers(app: FastAPI) -> None:
    add_exception_handler(
        app,
        new_exception_handler(
            logger=logging.getLogger(__name__),
            unhandled_wrappers={"default": UnexpectedError},
            post_hooks=[add_request_id],
            documentation_uri_template=ERROR_TYPE_URL,
        ),
    )
