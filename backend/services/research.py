"""Turn normalized data into one stable research response."""

from backend.providers.base import MarketDataProvider
from backend.schemas import OhlcCandle, ResearchResponse


def build_market_summary(change_percent: float, latest_close: float, first_close: float) -> str:
    """Create an explainable template summary; a future LLM can replace this function."""
    direction = "rose" if change_percent > 0 else "fell" if change_percent < 0 else "was unchanged"
    five_day_move = ((latest_close - first_close) / first_close) * 100
    return (
        f"Latest available price {direction} {abs(change_percent):.2f}% versus the previous close. "
        f"Over the displayed period, the closing price moved {five_day_move:+.2f}%. "
        "This is descriptive research, not trading advice."
    )


async def research_symbol(symbol: str, provider: MarketDataProvider) -> ResearchResponse:
    """Fetch data, calculate the percentage move, then validate the public API contract."""
    snapshot = await provider.fetch_daily_data(symbol)
    change_percent = ((snapshot.price - snapshot.previous_close) / snapshot.previous_close) * 100
    ohlc = [OhlcCandle(**candle) for candle in snapshot.candles]
    return ResearchResponse(
        symbol=snapshot.requested_symbol,
        provider_symbol=snapshot.provider_symbol,
        price=round(snapshot.price, 4),
        change_percent=round(change_percent, 2),
        ohlc=ohlc,
        summary=build_market_summary(change_percent, ohlc[-1].close, ohlc[0].close),
        source=provider.name,
        fetched_at=snapshot.fetched_at,
    )

