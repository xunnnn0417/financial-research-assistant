"""Yahoo Finance implementation of the provider interface.

Yahoo's public chart endpoint is used for this learning V1. It requires no API key,
but may rate-limit or change; those outcomes are handled by the service layer.
"""

from datetime import UTC, datetime
from urllib.parse import quote

import httpx

from backend.config import REQUEST_TIMEOUT_SECONDS
from backend.providers.base import MarketDataProvider, MarketSnapshot


class ProviderError(Exception):
    """Expected external-provider failure, safe to translate into an API error."""

    def __init__(self, message: str, code: str = "provider_unavailable"):
        super().__init__(message)
        self.code = code


class YahooProvider(MarketDataProvider):
    """Fetch recent daily OHLC data from Yahoo Finance's public chart endpoint."""

    name = "Yahoo Finance (public chart endpoint)"
    SYMBOL_ALIASES = {"XAUUSD": "XAUUSD=X"}

    def provider_symbol_for(self, symbol: str) -> str:
        """Map the friendly V1 gold symbol to Yahoo's FX ticker."""
        return self.SYMBOL_ALIASES.get(symbol.upper(), symbol.upper())

    async def fetch_daily_data(self, symbol: str) -> MarketSnapshot:
        """Request five daily candles and normalize Yahoo's column-oriented payload."""
        provider_symbol = self.provider_symbol_for(symbol)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(provider_symbol, safe='=')}"
        params = {"range": "10d", "interval": "1d"}
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.get(
                    url, params=params, headers={"User-Agent": "FinancialResearchAssistant/1.0"}
                )
        except httpx.TimeoutException as error:
            raise ProviderError("Market-data provider timed out. Please try again.") from error
        except httpx.HTTPError as error:
            raise ProviderError("Could not reach the market-data provider.") from error

        if response.status_code == 429:
            raise ProviderError(
                "Market-data provider rate limit reached. Please try again later.", "provider_rate_limited"
            )
        if response.status_code >= 400:
            raise ProviderError("Symbol was not found or market data is unavailable.", "invalid_symbol")

        try:
            result = response.json()["chart"]["result"][0]
            timestamps = result["timestamp"]
            quote_data = result["indicators"]["quote"][0]
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise ProviderError("Market-data provider returned an unexpected response.") from error

        candles = []
        for index, timestamp in enumerate(timestamps):
            values = {key: quote_data[key][index] for key in ("open", "high", "low", "close", "volume")}
            if any(values[key] is None for key in ("open", "high", "low", "close")):
                continue
            candles.append(
                {
                    "date": datetime.fromtimestamp(timestamp, UTC).date().isoformat(),
                    "open": float(values["open"]),
                    "high": float(values["high"]),
                    "low": float(values["low"]),
                    "close": float(values["close"]),
                    "volume": int(values["volume"]) if values["volume"] is not None else None,
                }
            )

        if len(candles) < 2:
            raise ProviderError(
                "Not enough recent OHLC data was available for this symbol.", "invalid_symbol"
            )
        metadata = result.get("meta", {})
        price = metadata.get("regularMarketPrice") or candles[-1]["close"]
        previous_close = metadata.get("chartPreviousClose") or candles[-2]["close"]
        if price is None or previous_close in (None, 0):
            raise ProviderError("Market-data provider did not include a usable latest price.")
        return MarketSnapshot(
            symbol.upper(),
            provider_symbol,
            float(price),
            float(previous_close),
            candles[-5:],
            datetime.now(UTC),
        )
