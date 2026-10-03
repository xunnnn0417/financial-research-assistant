"""FastAPI dependencies that can be replaced cleanly during tests."""

from backend.providers.base import MarketDataProvider
from backend.providers.market_data import YahooProvider


def get_market_data_provider() -> MarketDataProvider:
    """Return the live provider; tests override this dependency with a fake."""
    return YahooProvider()
