"""Pydantic models define the API contract sent to the browser."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class OhlcCandle(BaseModel):
    """One daily market-data candle."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int | None = None


class ResearchResponse(BaseModel):
    """Validated, provider-independent response for the research page."""

    symbol: str
    provider_symbol: str
    price: float
    change_percent: float
    ohlc: list[OhlcCandle] = Field(min_length=1, max_length=10)
    summary: str
    source: str
    fetched_at: datetime


class ErrorResponse(BaseModel):
    """Safe error body returned instead of an internal traceback."""

    detail: str
    code: Literal["invalid_symbol", "provider_unavailable", "provider_rate_limited"]

