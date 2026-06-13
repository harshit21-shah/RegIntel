"""Standard API error types per API_SPEC.md."""

from __future__ import annotations


class APIError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        request_id: str | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        super().__init__(message)


class NotFoundError(APIError):
    def __init__(
        self, message: str = "Resource not found", *, request_id: str | None = None
    ) -> None:
        super().__init__(code="NOT_FOUND", message=message, status_code=404, request_id=request_id)


class UnauthorizedError(APIError):
    def __init__(
        self, message: str = "Authentication required", *, request_id: str | None = None
    ) -> None:
        super().__init__(
            code="UNAUTHORIZED", message=message, status_code=401, request_id=request_id
        )


class ForbiddenError(APIError):
    def __init__(self, message: str = "Forbidden", *, request_id: str | None = None) -> None:
        super().__init__(code="FORBIDDEN", message=message, status_code=403, request_id=request_id)


class RateLimitError(APIError):
    def __init__(self, *, request_id: str | None = None) -> None:
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded. Retry later.",
            status_code=429,
            request_id=request_id,
        )


class CostBudgetError(APIError):
    def __init__(self, *, request_id: str | None = None) -> None:
        super().__init__(
            code="COST_BUDGET_EXCEEDED",
            message="Daily LLM cost budget exceeded for this tenant.",
            status_code=429,
            request_id=request_id,
        )


class ValidationError(APIError):
    def __init__(self, message: str, *, request_id: str | None = None) -> None:
        super().__init__(
            code="VALIDATION_ERROR", message=message, status_code=400, request_id=request_id
        )


class LLMBudgetExceededError(Exception):
    """Raised when per-request or daily LLM budget is exhausted."""
