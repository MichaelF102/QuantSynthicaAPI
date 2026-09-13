"""Multi-asset screener resource for stocks, crypto, forex, futures, bonds, CFDs."""

from typing import List, Optional, Dict, Any
from quantsynthica.resources.base import BaseResource, DotDict


class ScreenerResource(BaseResource):
    def query(
        self,
        market: str = "india",
        columns: Optional[List[str]] = None,
        sort_by: Optional[str] = "market_cap_basic",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> DotDict:
        """Execute custom stock screener with 3000+ column support and SQL-like filters."""
        payload = {
            "market": market,
            "columns": columns,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "limit": limit,
            "offset": offset,
            "filters": filters,
        }
        return self._request("POST", "screener/query", json_data=payload)

    def value_stocks(self, market: str = "india", limit: int = 50) -> DotDict:
        """Predefined screen: Value stocks."""
        return self._request("GET", "screener/value", params={"market": market, "limit": limit})

    def growth_stocks(self, market: str = "india", limit: int = 50) -> DotDict:
        """Predefined screen: High growth stocks."""
        return self._request("GET", "screener/growth", params={"market": market, "limit": limit})

    def momentum_stocks(self, market: str = "india", limit: int = 50) -> DotDict:
        """Predefined screen: Momentum stocks."""
        return self._request("GET", "screener/momentum", params={"market": market, "limit": limit})

    def dividend_stocks(self, market: str = "india", limit: int = 50) -> DotDict:
        """Predefined screen: High dividend yield stocks."""
        return self._request("GET", "screener/dividend", params={"market": market, "limit": limit})

    def crypto(self, limit: int = 50, sort_by: str = "volume") -> DotDict:
        """Screen centralized crypto pairs (CEX)."""
        return self._request("POST", "screener/crypto", json_data={"limit": limit, "sort_by": sort_by})

    def forex(self, limit: int = 50, sort_by: str = "volume") -> DotDict:
        """Screen foreign exchange currency pairs."""
        return self._request("POST", "screener/forex", json_data={"limit": limit, "sort_by": sort_by})

    def bonds(self, limit: int = 50) -> DotDict:
        """Screen sovereign and corporate bonds."""
        return self._request("POST", "screener/bonds", json_data={"limit": limit})

    def futures(self, limit: int = 50) -> DotDict:
        """Screen commodity and index futures."""
        return self._request("POST", "screener/futures", json_data={"limit": limit})

    def cfd(self, limit: int = 50) -> DotDict:
        """Screen CFD contracts."""
        return self._request("POST", "screener/cfd", json_data={"limit": limit})
