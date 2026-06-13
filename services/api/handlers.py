"""Global exception handlers and error response formatting."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.responses import Response

from services.api.exceptions import APIError


def error_payload(exc: APIError) -> dict[str, Any]:
    return {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "request_id": exc.request_id,
        }
    }


def error_response(exc: APIError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=error_payload(exc))


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> Response:
        from services.api.exceptions import APIError

        code = "UNAUTHORIZED" if exc.status_code == 401 else "HTTP_ERROR"
        if exc.status_code == 403:
            code = "FORBIDDEN"
        elif exc.status_code == 404:
            code = "NOT_FOUND"
        api_exc = APIError(
            code=code,
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=getattr(request.state, "request_id", None),
        )
        return error_response(api_exc)

    @app.exception_handler(APIError)
    async def handle_api_error(request: Request, exc: APIError) -> Response:
        if exc.request_id is None:
            exc.request_id = getattr(request.state, "request_id", None)
        return error_response(exc)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError) -> Response:
        from services.api.exceptions import ValidationError

        message = "; ".join(
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()
        )
        api_exc = ValidationError(message, request_id=getattr(request.state, "request_id", None))
        return error_response(api_exc)

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> Response:
        import logging

        logging.getLogger(__name__).exception("Unhandled exception", exc_info=exc)
        from services.api.exceptions import APIError

        api_exc = APIError(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred.",
            status_code=500,
            request_id=getattr(request.state, "request_id", None),
        )
        return error_response(api_exc)
