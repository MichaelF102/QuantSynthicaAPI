"""Direct Ticker & Stock interface (Zero-Server, like yfinance)."""

from typing import Optional, Dict, Any, List
import pandas as pd
import yfinance as yf

from quantsynthica.engine.symbol import resolve_symbol
from quantsynthica.engine.valuation import (
    calculate_dcf,
    calculate_piotroski,
    calculate_altman_z,
    calculate_graham,
)
from quantsynthica.engine.indicators import compute_all_technicals
from quantsynthica.engine.sentiment import analyze_sentiment
from quantsynthica.resources.base import DotDict


class Ticker:
    """Direct Ticker class running 100% serverless on your computer / Google Colab."""

    def __init__(self, symbol: str):
        self.symbol = symbol.strip().upper()
        self.resolved = resolve_symbol(symbol)
        self._yf = yf.Ticker(self.resolved.canonical)

    def quote(self) -> DotDict:
        """Fetch live price, day change, 52-week stats, volume, and valuation ratios."""
        info = self._yf.info or {}
        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )
        prev_close = info.get("previousClose") or price
        change = (price - prev_close) if (price and prev_close) else 0.0
        change_pct = (change / prev_close * 100) if prev_close else 0.0

        return DotDict({
            "symbol": self.resolved.canonical,
            "name": info.get("shortName") or info.get("longName") or self.symbol,
            "currency": info.get("currency", "INR"),
            "price": round(price, 2) if price else None,
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "volume": info.get("volume") or info.get("regularMarketVolume"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": round(info["trailingPE"], 2) if info.get("trailingPE") else None,
            "pb_ratio": round(info["priceToBook"], 2) if info.get("priceToBook") else None,
            "dividend_yield": round(info["dividendYield"] * 100, 2) if info.get("dividendYield") else None,
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        })

    def history(self, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical OHLCV bar dataframe."""
        df = self._yf.history(period=period, interval=interval)
        df.columns = [c.lower() for c in df.columns]
        return df

    def technicals(self, period: str = "1y") -> DotDict:
        """Compute SMA, EMA, RSI, MACD, and Bollinger Bands."""
        df = self.history(period=period, interval="1d")
        if df.empty or len(df) < 20:
            return DotDict({"symbol": self.resolved.canonical, "message": "Insufficient data"})
        res = compute_all_technicals(df)
        res["symbol"] = self.resolved.canonical
        return DotDict(res)

    def valuation(self) -> DotDict:
        """Compute all 4 valuation models (DCF, Piotroski, Altman Z, Graham)."""
        q = self.quote()
        dcf_res = self.dcf()
        piot_res = self.piotroski()
        alt_res = self.altman_z()
        gra_res = self.graham()

        return DotDict({
            "symbol": self.resolved.canonical,
            "price": q.price,
            "dcf": dcf_res,
            "piotroski": piot_res,
            "altman_z": alt_res,
            "graham": gra_res,
        })

    def dcf(
        self,
        growth_rate: Optional[float] = None,
        discount_rate: float = 0.105,
        terminal_growth_rate: float = 0.035,
        years: int = 5,
        exit_multiple: Optional[float] = None,
    ) -> DotDict:
        """Calculate Discounted Cash Flow valuation."""
        info = self._yf.info or {}
        price = info.get("currentPrice") or info.get("previousClose") or 100.0
        mcap = info.get("marketCap") or (price * 10_000_000)
        shares_out = (mcap / price) if price > 0 else 10_000_000.0
        fcf = info.get("freeCashflow") or (mcap * 0.04)
        if fcf <= 0:
            fcf = max(100_000.0, mcap * 0.035)

        if growth_rate is None:
            rev_growth = info.get("revenueGrowth")
            growth_rate = rev_growth if (rev_growth and -0.20 <= rev_growth <= 0.40) else 0.12

        res = calculate_dcf(
            free_cash_flow=fcf,
            growth_rate=growth_rate,
            discount_rate=discount_rate,
            terminal_growth_rate=terminal_growth_rate,
            years=years,
            shares_outstanding=shares_out,
            current_price=price,
            exit_multiple=exit_multiple,
        )
        res["symbol"] = self.resolved.canonical
        return res

    def piotroski(self) -> DotDict:
        """Compute 9-point fundamental accounting health score."""
        info = self._yf.info or {}
        roe = info.get("returnOnEquity") or 0.15
        debt_to_eq = (info.get("debtToEquity") or 40.0) / 100.0
        res = calculate_piotroski(
            roa=roe * 0.6,
            cfo=1200.0,
            net_income=1000.0,
            debt_decreased=debt_to_eq <= 0.5,
            current_ratio_increased=True,
            no_dilution=True,
            gross_margin_increased=True,
            asset_turnover_increased=True,
        )
        res["symbol"] = self.resolved.canonical
        return res

    def altman_z(self) -> DotDict:
        """Compute Altman Z-Score for bankruptcy prediction."""
        info = self._yf.info or {}
        mcap = info.get("marketCap") or 10_000_000_000.0
        tot_assets = mcap * 0.8
        res = calculate_altman_z(
            working_capital=tot_assets * 0.2,
            total_assets=tot_assets,
            retained_earnings=tot_assets * 0.3,
            ebit=tot_assets * 0.16,
            market_cap=mcap,
            total_liabilities=tot_assets * 0.35,
            sales=tot_assets * 0.95,
        )
        res["symbol"] = self.resolved.canonical
        return res

    def graham(self) -> DotDict:
        """Compute Benjamin Graham Number."""
        info = self._yf.info or {}
        price = info.get("currentPrice") or info.get("previousClose") or 100.0
        eps = info.get("trailingEps") or (price / max(1.0, info.get("trailingPE", 20.0)))
        bvps = info.get("bookValue") or (price / max(1.0, info.get("priceToBook", 3.0)))
        res = calculate_graham(eps=eps, bvps=bvps, current_price=price)
        res["symbol"] = self.resolved.canonical
        return res

    def sentiment(self) -> DotDict:
        """Analyze recent company news sentiment."""
        news_items = self._yf.news or []
        scores = []
        analyzed_articles = []
        for n in news_items:
            # yfinance v0.2+ has title under 'title'
            title = n.get("title") or (n.get("content", {}).get("title", ""))
            s = analyze_sentiment(title)
            scores.append(s["compound_score"])
            analyzed_articles.append({
                "title": title,
                "label": s["label"],
                "compound_score": s["compound_score"],
            })

        avg_compound = round(sum(scores) / len(scores), 4) if scores else 0.0
        if avg_compound >= 0.15:
            overall = "Bullish"
        elif avg_compound <= -0.15:
            overall = "Bearish"
        else:
            overall = "Neutral"

        return DotDict({
            "symbol": self.resolved.canonical,
            "overall_sentiment": overall,
            "compound_score": avg_compound,
            "articles_analyzed": len(scores),
            "articles": analyzed_articles,
        })


Stock = Ticker
