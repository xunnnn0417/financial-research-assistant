"""API-level test: route, service, schema, and error contract work together."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.dependencies import get_market_data_provider
from backend.main import app
from backend.providers.base import MarketSnapshot


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
