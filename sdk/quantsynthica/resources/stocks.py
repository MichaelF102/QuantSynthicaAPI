"""Unified stock profiles and system search resource."""

from quantsynthica.resources.base import BaseResource, DotDict


class StocksResource(BaseResource):
    def get_profile(self, symbol: str) -> DotDict:
        """Get 360-degree unified stock profile (Identity + Market + Fundamentals + Quant)."""
        return self._request("GET", f"stocks/{symbol}")

    def search(self, query: str) -> DotDict:
        """Search and resolve stock symbols across NSE, BSE, and US tickers."""
        return self._request("GET", "search", params={"q": query})

    def health(self) -> DotDict:
        """Check API provider health and system status."""
        return self._request("GET", "health")
