"""Provider interface: the rest of the app does not depend on Yahoo details."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketSnapshot:
    """Normalized provider data before it enters the response schema."""

    requested_symbol: str
    provider_symbol: str
    price: float
    previous_close: float
    candles: list[dict]
    updated_at: datetime


class MarketDataProvider(ABC):
    """Small replacement seam for a future Alpha Vantage or Twelve Data provider."""

    name: str

    @abstractmethod
    async def fetch_daily_data(self, symbol: str) -> MarketSnapshot:
        """Fetch, normalize, and return daily data for one user-facing symbol."""
