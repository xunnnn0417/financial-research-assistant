"""API-level test: route, service, schema, and error contract work together."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.dependencies import get_market_data_provider
from backend.main import app
from backend.providers.base import MarketSnapshot
from backend.providers.market_data import ProviderError


class FakeProvider:
    """Deterministic provider used so this test never needs the internet."""

    name = "Fake Provider"

    async def fetch_daily_data(self, symbol: str) -> MarketSnapshot:
        return MarketSnapshot(
            symbol,
            symbol,
            110.0,
            100.0,
            [
                {
                    "date": "2026-01-01",
                    "open": 99.0,
                    "high": 102.0,
                    "low": 98.0,
                    "close": 100.0,
                    "volume": 100,
                },
                {
                    "date": "2026-01-02",
                    "open": 101.0,
                    "high": 112.0,
                    "low": 100.0,
                    "close": 110.0,
                    "volume": 200,
                },
            ],
            datetime.now(UTC),
        )


def test_research_endpoint_returns_stable_contract():
    app.dependency_overrides[get_market_data_provider] = lambda: FakeProvider()
    try:
        response = TestClient(app).get("/api/research/AAPL")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["price"] == 110.0
    assert body["change_percent"] == 10.0
    assert len(body["ohlc"]) == 2
    assert body["source"] == "Fake Provider"
    assert "fetched_at" in body


class FailingProvider:
    name = "Failing Provider"

    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code

    async def fetch_daily_data(self, _: str) -> MarketSnapshot:
        raise ProviderError(self.message, self.code)


def test_invalid_symbol_returns_documented_error_body():
    response = TestClient(app).get("/api/research/%40%40%40%40")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Use a short market symbol such as AAPL, NVDA, or XAUUSD.",
        "code": "invalid_symbol",
    }


def test_provider_unavailable_returns_502_with_safe_message():
    app.dependency_overrides[get_market_data_provider] = lambda: FailingProvider(
        "Could not reach the market-data provider.", "provider_unavailable"
    )
    try:
        response = TestClient(app).get("/api/research/AAPL")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Could not reach the market-data provider.",
        "code": "provider_unavailable",
    }


def test_provider_rate_limit_returns_503_with_safe_message():
    app.dependency_overrides[get_market_data_provider] = lambda: FailingProvider(
        "Market-data provider rate limit reached. Please try again later.", "provider_rate_limited"
    )
    try:
        response = TestClient(app).get("/api/research/AAPL")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Market-data provider rate limit reached. Please try again later.",
        "code": "provider_rate_limited",
    }

