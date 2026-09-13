"""Valuation resource for DCF, Piotroski F-Score, Altman Z-Score, and Graham Number."""

from typing import Optional
from quantsynthica.resources.base import BaseResource, DotDict


class ValuationResource(BaseResource):
    def get_overview(self, symbol: str) -> DotDict:
        """Get comprehensive valuation overview combining DCF, Piotroski, Altman Z, and Graham Number."""
        return self._request("GET", f"valuation/{symbol}")

    def dcf(
        self,
        symbol: str,
        growth_rate: Optional[float] = None,
        discount_rate: Optional[float] = None,
        terminal_growth_rate: Optional[float] = None,
        years: int = 5,
        exit_multiple: Optional[float] = None,
    ) -> DotDict:
        """Run custom Discounted Cash Flow valuation."""
        payload = {
            "symbol": symbol,
            "growth_rate": growth_rate,
            "discount_rate": discount_rate,
            "terminal_growth_rate": terminal_growth_rate,
            "years": years,
            "exit_multiple": exit_multiple,
        }
        return self._request("POST", "valuation/dcf", json_data=payload)

    def piotroski(self, symbol: str) -> DotDict:
        """Get Piotroski 9-point fundamental financial health score."""
        return self._request("GET", f"valuation/piotroski/{symbol}")

    def altman_z(self, symbol: str) -> DotDict:
        """Get Altman Z-Score and bankruptcy distress categorization."""
        return self._request("GET", f"valuation/altman-z/{symbol}")

    def graham(self, symbol: str) -> DotDict:
        """Get Benjamin Graham Number & Net-Net valuation."""
        return self._request("GET", f"valuation/graham/{symbol}")
