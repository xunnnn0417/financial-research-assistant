"""Small application-error type and one consistent JSON error handler."""

from fastapi import Request
from fastapi.responses import JSONResponse


class ResearchError(Exception):
    """Expected request or provider error that is safe to show to a visitor."""

    def __init__(self, status_code: int, detail: str, code: str):
        self.status_code = status_code
        self.detail = detail
        self.code = code


async def research_error_handler(_: Request, error: ResearchError) -> JSONResponse:
    """Keep every expected failure in the documented {detail, code} shape."""
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail, "code": error.code})
