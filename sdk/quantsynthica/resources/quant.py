"""Quantitative analytics resource for returns, risk, volatility, and technicals."""

from quantsynthica.resources.base import BaseResource, DotDict


class QuantResource(BaseResource):
    def get_returns(self, symbol: str, period: str = "1y") -> DotDict:
        """Get daily returns, cumulative return, CAGR, and momentum series."""
        return self._request("GET", f"quant/{symbol}/returns", params={"period": period})

    def get_risk(self, symbol: str, period: str = "1y", risk_free_rate: float = 0.05) -> DotDict:
        """Get volatility, Sharpe, Sortino, Max Drawdown, VaR 95%, CVaR 95%, Beta, Alpha."""
        return self._request("GET", f"quant/{symbol}/risk", params={"period": period, "risk_free_rate": risk_free_rate})

    def get_volatility(self, symbol: str, period: str = "1y") -> DotDict:
        """Get daily, annualized, rolling 20d, Parkinson volatility, and ATR."""
        return self._request("GET", f"quant/{symbol}/volatility", params={"period": period})

    def get_summary(self, symbol: str, period: str = "1y") -> DotDict:
        """Get combined Returns + Risk + Technical indicators summary."""
        return self._request("GET", f"quant/{symbol}/summary", params={"period": period})

    def get_technical(self, symbol: str, period: str = "1y") -> DotDict:
        """Get technical indicator indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, VWAP)."""
        return self._request("GET", f"technical/{symbol}", params={"period": period})
