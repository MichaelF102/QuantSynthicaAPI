"""Market data resource for quotes, history, dividends, options, news."""

from typing import Any, Optional
from quantsynthica.resources.base import BaseResource, DotDict


class MarketResource(BaseResource):
    def get_quote(self, symbol: str) -> DotDict:
        """Get live or latest price quote for a symbol."""
        return self._request("GET", f"market/{symbol}/quote")

    def get_history(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> DotDict:
        """Get historical OHLCV candles."""
        params = {
            "period": period,
            "interval": interval,
            "start_date": start_date,
            "end_date": end_date,
        }
        return self._request("GET", f"market/{symbol}/history", params=params)

    def get_dividends(self, symbol: str) -> DotDict:
        """Get historical dividend payouts."""
        return self._request("GET", f"market/{symbol}/dividends")

    def get_splits(self, symbol: str) -> DotDict:
        """Get stock split actions."""
        return self._request("GET", f"market/{symbol}/splits")

    def get_recommendations(self, symbol: str) -> DotDict:
        """Get Wall Street consensus recommendations and price targets."""
        return self._request("GET", f"market/{symbol}/recommendations")

    def get_upgrades_downgrades(self, symbol: str) -> DotDict:
        """Get analyst upgrade/downgrade history."""
        return self._request("GET", f"market/{symbol}/upgrades-downgrades")

    def get_options_chain(self, symbol: str, date: Optional[str] = None) -> DotDict:
        """Get options chain with Calls & Puts."""
        params = {"date": date} if date else None
        return self._request("GET", f"market/{symbol}/options", params=params)

    def get_news(self, symbol: str) -> DotDict:
        """Get latest real-time company news feed."""
        return self._request("GET", f"market/{symbol}/news")
