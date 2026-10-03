import asyncio
from datetime import UTC, datetime

from backend.providers.base import MarketSnapshot
from backend.services.research import research_symbol


class FakeProvider:
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


def test_research_response_is_validated_schema():
    response = asyncio.run(research_symbol("AAPL", FakeProvider()))
    assert response.symbol == "AAPL"
    assert response.price == 110.0
    assert response.change_percent == 10.0
    assert len(response.ohlc) == 2
