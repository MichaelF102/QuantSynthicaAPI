"""Direct TradingView multi-asset screener (No server required)."""

from typing import List, Optional, Dict, Any
import pandas as pd
from tradingview_screener import Query, Column
from quantsynthica.resources.base import DotDict


class DirectScreener:
    """Direct TradingView screener running locally on your computer/Colab."""

    @staticmethod
    def query(
        market: str = "india",
        columns: Optional[List[str]] = None,
        sort_by: str = "market_cap_basic",
        sort_order: str = "desc",
        limit: int = 50,
    ) -> DotDict:
        if not columns:
            columns = ["name", "close", "change", "volume", "market_cap_basic", "price_earnings_ttm"]

        q = Query().set_markets(market).select(*columns)
        if sort_order.lower() == "desc":
            q.order_by(sort_by, ascending=False)
        else:
            q.order_by(sort_by, ascending=True)

        q.limit(limit)
        count, df = q.get_scanner_data()

        records = df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else []
        return DotDict({
            "count": count,
            "data": records,
        })

    @staticmethod
    def value_stocks(market: str = "india", limit: int = 50) -> DotDict:
        """Screen for undervalued, profitable stocks (low P/E, positive ROE)."""
        q = (
            Query()
            .set_markets(market)
            .select("name", "close", "change", "price_earnings_ttm", "return_on_equity", "market_cap_basic")
            .where(
                Column("price_earnings_ttm").between(0.01, 25),
                Column("market_cap_basic") > 1_000_000_000,
            )
            .order_by("price_earnings_ttm", ascending=True)
            .limit(limit)
        )
        count, df = q.get_scanner_data()
        records = df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else []
        return DotDict({"count": count, "data": records})

    @staticmethod
    def growth_stocks(market: str = "india", limit: int = 50) -> DotDict:
        """Screen for high revenue and earnings growth stocks."""
        q = (
            Query()
            .set_markets(market)
            .select("name", "close", "change", "total_revenue_yoy_growth_ttm", "market_cap_basic")
            .where(Column("total_revenue_yoy_growth_ttm") > 15)
            .order_by("total_revenue_yoy_growth_ttm", ascending=False)
            .limit(limit)
        )
        count, df = q.get_scanner_data()
        records = df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else []
        return DotDict({"count": count, "data": records})

    @staticmethod
    def crypto(limit: int = 50, sort_by: str = "volume") -> DotDict:
        """Screen centralized crypto market pairs."""
        from tradingview_screener.crypto import CryptoQuery
        q = CryptoQuery().select("name", "close", "change", "volume").order_by(sort_by, ascending=False).limit(limit)
        count, df = q.get_scanner_data()
        records = df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else []
        return DotDict({"count": count, "data": records})

    @staticmethod
    def forex(limit: int = 50, sort_by: str = "volume") -> DotDict:
        """Screen foreign exchange currency pairs."""
        from tradingview_screener.forex import ForexQuery
        q = ForexQuery().select("name", "close", "change", "volume").order_by(sort_by, ascending=False).limit(limit)
        count, df = q.get_scanner_data()
        records = df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else []
        return DotDict({"count": count, "data": records})


screener = DirectScreener()
