"""FastAPI entry point and static frontend host."""

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import FRONTEND_DIR
from backend.dependencies import get_market_data_provider
from backend.errors import ResearchError, research_error_handler
from backend.providers.base import MarketDataProvider
from backend.providers.market_data import ProviderError
from backend.schemas import ErrorResponse, ResearchResponse
from backend.services.research import research_symbol

app = FastAPI(title="Financial Research Assistant", version="1.0.0")
app.add_exception_handler(ResearchError, research_error_handler)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple check that the API server is running."""
    return {"status": "ok"}


@app.get(
    "/api/research/{symbol}",
    response_model=ResearchResponse,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def research(
    symbol: str,
    market_data_provider: Annotated[MarketDataProvider, Depends(get_market_data_provider)],
) -> ResearchResponse:
    """Return validated research data and safe errors for a requested market symbol."""
    clean_symbol = symbol.strip().upper()
    if (
        not clean_symbol
        or len(clean_symbol) > 20
        or not all(char.isalnum() or char in "=.-^" for char in clean_symbol)
    ):
        raise ResearchError(400, "Use a short market symbol such as AAPL, NVDA, or XAUUSD.", "invalid_symbol")
    try:
        return await research_symbol(clean_symbol, market_data_provider)
    except ProviderError as error:
        status = (
            400 if error.code == "invalid_symbol" else 503 if error.code == "provider_rate_limited" else 502
        )
        raise ResearchError(status, str(error), error.code) from error


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    """Serve the frontend from the same origin as the API."""
    return FileResponse(FRONTEND_DIR / "index.html")
