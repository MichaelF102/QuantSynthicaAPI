"""Main Client class for the QuantSynthica Python SDK."""

import os
from typing import Optional
import httpx

from quantsynthica.resources.market import MarketResource
from quantsynthica.resources.fundamentals import FundamentalsResource
from quantsynthica.resources.screener import ScreenerResource
from quantsynthica.resources.quant import QuantResource
from quantsynthica.resources.valuation import ValuationResource
from quantsynthica.resources.portfolio import PortfolioResource
from quantsynthica.resources.sentiment import SentimentResource
from quantsynthica.resources.reports import ReportsResource
from quantsynthica.resources.stocks import StocksResource


class QuantSynthica:
    """Official Python Client for the QuantSynthica Market & Quantitative Finance API.

    Usage:
        >>> from quantsynthica import QuantSynthica
        >>> client = QuantSynthica(api_key="your_key", base_url="http://localhost:8000")
        >>> quote = client.market.get_quote("RELIANCE")
        >>> print(quote.data.price)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        http_client: Optional[httpx.Client] = None,
    ):
        self.api_key = api_key or os.getenv("QUANTSYNTHICA_API_KEY")
        self.base_url = (base_url or os.getenv("QUANTSYNTHICA_BASE_URL", "http://localhost:8000")).rstrip("/")
        self.timeout = timeout
        self.version = "1.0.0"

        self._http_client = http_client or httpx.Client(timeout=self.timeout)
        self._owns_http_client = http_client is None

        # Resource Namespaces
        self.market = MarketResource(self)
        self.fundamentals = FundamentalsResource(self)
        self.screener = ScreenerResource(self)
        self.quant = QuantResource(self)
        self.valuation = ValuationResource(self)
        self.portfolio = PortfolioResource(self)
        self.sentiment = SentimentResource(self)
        self.reports = ReportsResource(self)
        self.stocks = StocksResource(self)

    # Shorthand aliases for convenience
    def quote(self, symbol: str):
        return self.market.get_quote(symbol)

    def history(self, symbol: str, period: str = "1y", interval: str = "1d"):
        return self.market.get_history(symbol, period=period, interval=interval)

    def valuation_overview(self, symbol: str):
        return self.valuation.get_overview(symbol)

    def search(self, query: str):
        return self.stocks.search(query)

    def close(self):
        if self._owns_http_client:
            self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Alias for intuitive importing
Client = QuantSynthica
