import sys
import time
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.logging import logger
from quant_synthica_api.providers.base import BaseProvider, ProviderResult
from quant_synthica_api.schemas.market import (
    QuoteData, OHLCVItem, HistoryResponse, DividendItem, DividendsResponse,
    SplitItem, SplitsResponse, AnalystRecommendationsResponse, RecommendationItem,
    PriceTargetData, UpgradesDowngradesResponse, UpgradeDowngradeItem,
    OptionsChainResponse, OptionContractItem, NewsResponse, NewsItem
)
from quant_synthica_api.schemas.fundamentals import (
    FinancialStatementData, FinancialRow, HoldersResponse, HolderItem,
    InsiderTransactionsResponse, InsiderTransactionItem, SustainabilityResponse, ESGRatingsData
)
from quant_synthica_api.utils.rate_limiter import SyncThrottle

# Ensure local yfinance repository is imported safely
settings = get_settings()
yfinance_path_str = str(settings.YFINANCE_DIR)
if yfinance_path_str not in sys.path:
    sys.path.insert(0, yfinance_path_str)

import yfinance as yf

class YFinanceProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="yfinance")
        self.throttle = SyncThrottle(min_interval=settings.YFINANCE_MIN_INTERVAL)

    def health_check(self) -> bool:
        try:
            return hasattr(yf, "Ticker")
        except Exception:
            return False

    def _get_ticker(self, symbol: str) -> yf.Ticker:
        self.throttle.acquire()
        return yf.Ticker(symbol)

    def get_quote(self, symbol: str) -> ProviderResult[QuoteData]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            info = ticker.info or {}
            
            price = (
                info.get("currentPrice") or 
                info.get("regularMarketPrice") or 
                info.get("previousClose")
            )
            
            if price is None:
                fast = getattr(ticker, "fast_info", None)
                if fast:
                    try:
                        price = float(fast.last_price or fast.previous_close)
                    except Exception:
                        pass

            if price is None:
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])

            prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
            change = (price - prev_close) if (price is not None and prev_close is not None) else None
            change_percent = ((change / prev_close) * 100.0) if (change is not None and prev_close) else None

            quote = QuoteData(
                symbol=symbol,
                name=info.get("shortName") or info.get("longName") or symbol,
                exchange=info.get("exchange"),
                currency=info.get("currency", "INR"),
                price=round(float(price), 4) if price is not None else None,
                open=float(info.get("regularMarketOpen") or info.get("open") or 0.0) or None,
                high=float(info.get("regularMarketDayHigh") or info.get("dayHigh") or 0.0) or None,
                low=float(info.get("regularMarketDayLow") or info.get("dayLow") or 0.0) or None,
                previous_close=float(prev_close) if prev_close is not None else None,
                change=round(float(change), 4) if change is not None else None,
                change_percent=round(float(change_percent), 4) if change_percent is not None else None,
                volume=int(info.get("regularMarketVolume") or info.get("volume") or 0) or None,
                avg_volume=int(info.get("averageVolume") or 0) or None,
                market_cap=float(info.get("marketCap") or 0.0) or None,
                pe_ratio=float(info.get("trailingPE") or info.get("forwardPE") or 0.0) or None,
                dividend_yield=float(info.get("dividendYield") or 0.0) or None,
                fifty_two_week_high=float(info.get("fiftyTwoWeekHigh") or 0.0) or None,
                fifty_two_week_low=float(info.get("fiftyTwoWeekLow") or 0.0) or None,
            )
            return ProviderResult(
                data=quote, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000
            )
        except Exception as e:
            logger.error(f"yfinance get_quote failed for {symbol}: {e}")
            return ProviderResult(
                data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000
            )

    def get_history(
        self, symbol: str, period: str = "1mo", interval: str = "1d", start: Optional[str] = None, end: Optional[str] = None
    ) -> ProviderResult[List[OHLCVItem]]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            if start:
                df = ticker.history(start=start, end=end, interval=interval)
            else:
                df = ticker.history(period=period, interval=interval)

            if df is None or df.empty:
                return ProviderResult(data=[], provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)

            items: List[OHLCVItem] = []
            for dt, row in df.iterrows():
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, "strftime") else str(dt)
                adj = float(row["Adj Close"]) if "Adj Close" in row and not pd.isna(row["Adj Close"]) else float(row["Close"])
                items.append(OHLCVItem(
                    date=date_str,
                    open=round(float(row["Open"]), 4),
                    high=round(float(row["High"]), 4),
                    low=round(float(row["Low"]), 4),
                    close=round(float(row["Close"]), 4),
                    adj_close=round(adj, 4),
                    volume=int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
                ))

            return ProviderResult(data=items, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            logger.error(f"yfinance get_history failed for {symbol}: {e}")
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_dividends(self, symbol: str) -> ProviderResult[List[DividendItem]]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            div_series = ticker.dividends
            items: List[DividendItem] = []
            if div_series is not None and not div_series.empty:
                for dt, val in div_series.items():
                    items.append(DividendItem(
                        date=dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt),
                        dividend=round(float(val), 4)
                    ))
            return ProviderResult(data=items, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_splits(self, symbol: str) -> ProviderResult[List[SplitItem]]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            split_series = ticker.splits
            items: List[SplitItem] = []
            if split_series is not None and not split_series.empty:
                for dt, val in split_series.items():
                    items.append(SplitItem(
                        date=dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt),
                        split_ratio=round(float(val), 4)
                    ))
            return ProviderResult(data=items, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def _convert_df_to_statement(self, df: Optional[pd.DataFrame], statement_type: str) -> FinancialStatementData:
        if df is None or df.empty:
            return FinancialStatementData(statement_type=statement_type, periods=[], rows=[])
        
        periods = [d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d) for d in df.columns]
        rows: List[FinancialRow] = []
        for metric, row in df.iterrows():
            vals: Dict[str, Optional[float]] = {}
            for col, period_key in zip(df.columns, periods):
                val = row[col]
                vals[period_key] = round(float(val), 2) if not pd.isna(val) else None
            rows.append(FinancialRow(metric=str(metric), values=vals))
        
        return FinancialStatementData(statement_type=statement_type, periods=periods, rows=rows)

    def get_income_statement(self, symbol: str, quarterly: bool = False) -> ProviderResult[FinancialStatementData]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            df = ticker.quarterly_income_stmt if quarterly else ticker.income_stmt
            stmt = self._convert_df_to_statement(df, "income_statement")
            return ProviderResult(data=stmt, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_balance_sheet(self, symbol: str, quarterly: bool = False) -> ProviderResult[FinancialStatementData]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            df = ticker.quarterly_balance_sheet if quarterly else ticker.balance_sheet
            stmt = self._convert_df_to_statement(df, "balance_sheet")
            return ProviderResult(data=stmt, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_cash_flow(self, symbol: str, quarterly: bool = False) -> ProviderResult[FinancialStatementData]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            df = ticker.quarterly_cashflow if quarterly else ticker.cashflow
            stmt = self._convert_df_to_statement(df, "cash_flow")
            return ProviderResult(data=stmt, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_info(self, symbol: str) -> ProviderResult[Dict[str, Any]]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            info = ticker.info or {}
            return ProviderResult(data=info, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_options(self, symbol: str) -> ProviderResult[List[str]]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            dates = list(ticker.options or [])
            return ProviderResult(data=dates, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    # --- Extended yfinance Features ---

    def get_recommendations(self, symbol: str) -> ProviderResult[AnalystRecommendationsResponse]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            recs_df = ticker.recommendations
            items = []
            consensus = None
            if recs_df is not None and not recs_df.empty:
                for _, r in recs_df.iterrows():
                    items.append(RecommendationItem(
                        period=str(r.get("period", "")),
                        strong_buy=int(r.get("strongBuy", 0)) if not pd.isna(r.get("strongBuy")) else 0,
                        buy=int(r.get("buy", 0)) if not pd.isna(r.get("buy")) else 0,
                        hold=int(r.get("hold", 0)) if not pd.isna(r.get("hold")) else 0,
                        sell=int(r.get("sell", 0)) if not pd.isna(r.get("sell")) else 0,
                        strong_sell=int(r.get("strongSell", 0)) if not pd.isna(r.get("strongSell")) else 0
                    ))

            targets = ticker.analyst_price_targets or {}
            target_obj = None
            if targets:
                target_obj = PriceTargetData(
                    current=float(targets.get("current", 0.0)) or None,
                    low=float(targets.get("low", 0.0)) or None,
                    high=float(targets.get("high", 0.0)) or None,
                    mean=float(targets.get("mean", 0.0)) or None,
                    median=float(targets.get("median", 0.0)) or None
                )

            info = ticker.info or {}
            consensus = info.get("recommendationKey")

            resp = AnalystRecommendationsResponse(
                symbol=symbol,
                target_price=target_obj,
                recommendations=items,
                consensus=consensus,
                metadata={
                    "source": self.name,
                    "retrieved_at": pd.Timestamp.now("UTC").isoformat(),
                    "cached": False,
                    "latency_ms": (time.monotonic() - t0) * 1000
                }
            )
            return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_upgrades_downgrades(self, symbol: str, limit: int = 25) -> ProviderResult[UpgradesDowngradesResponse]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            df = ticker.upgrades_downgrades
            items = []
            if df is not None and not df.empty:
                for dt, r in df.head(limit).iterrows():
                    items.append(UpgradeDowngradeItem(
                        date=str(dt),
                        firm=str(r.get("Firm", "")) if not pd.isna(r.get("Firm")) else None,
                        to_grade=str(r.get("ToGrade", "")) if not pd.isna(r.get("ToGrade")) else None,
                        from_grade=str(r.get("FromGrade", "")) if not pd.isna(r.get("FromGrade")) else None,
                        action=str(r.get("Action", "")) if not pd.isna(r.get("Action")) else None
                    ))
            resp = UpgradesDowngradesResponse(
                symbol=symbol,
                count=len(items),
                items=items,
                metadata={
                    "source": self.name,
                    "retrieved_at": pd.Timestamp.now("UTC").isoformat(),
                    "cached": False,
                    "latency_ms": (time.monotonic() - t0) * 1000
                }
            )
            return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_option_chain(self, symbol: str, date: Optional[str] = None) -> ProviderResult[OptionsChainResponse]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            options = ticker.options
            if not options:
                return ProviderResult(data=None, provider=self.name, success=False, error=f"No options available for {symbol}", latency_ms=(time.monotonic() - t0) * 1000)

            exp_date = date if (date and date in options) else options[0]
            chain = ticker.option_chain(exp_date)

            def _parse_contracts(df):
                res = []
                if df is not None and not df.empty:
                    for _, r in df.iterrows():
                        res.append(OptionContractItem(
                            contract_symbol=str(r.get("contractSymbol", "")),
                            strike=float(r.get("strike", 0.0)),
                            last_price=float(r.get("lastPrice")) if not pd.isna(r.get("lastPrice")) else None,
                            bid=float(r.get("bid")) if not pd.isna(r.get("bid")) else None,
                            ask=float(r.get("ask")) if not pd.isna(r.get("ask")) else None,
                            change=float(r.get("change")) if not pd.isna(r.get("change")) else None,
                            percent_change=float(r.get("percentChange")) if not pd.isna(r.get("percentChange")) else None,
                            volume=int(r.get("volume")) if not pd.isna(r.get("volume")) else None,
                            open_interest=int(r.get("openInterest")) if not pd.isna(r.get("openInterest")) else None,
                            implied_volatility=round(float(r.get("impliedVolatility")), 4) if not pd.isna(r.get("impliedVolatility")) else None,
                            in_the_money=bool(r.get("inTheMoney")) if not pd.isna(r.get("inTheMoney")) else None
                        ))
                return res

            calls = _parse_contracts(chain.calls)
            puts = _parse_contracts(chain.puts)

            resp = OptionsChainResponse(
                symbol=symbol,
                expiration_date=exp_date,
                all_expirations=list(options),
                calls=calls,
                puts=puts,
                metadata={
                    "source": self.name,
                    "retrieved_at": pd.Timestamp.now("UTC").isoformat(),
                    "cached": False,
                    "latency_ms": (time.monotonic() - t0) * 1000
                }
            )
            return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_news(self, symbol: str) -> ProviderResult[NewsResponse]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            news_raw = ticker.news or []
            items = []
            for n in news_raw:
                items.append(NewsItem(
                    id=n.get("uuid") or n.get("id"),
                    title=n.get("title", ""),
                    publisher=n.get("publisher"),
                    link=n.get("link", ""),
                    published_at=str(n.get("providerPublishTime")) if n.get("providerPublishTime") else None,
                    type=n.get("type")
                ))
            resp = NewsResponse(
                symbol=symbol,
                count=len(items),
                news=items,
                metadata={
                    "source": self.name,
                    "retrieved_at": pd.Timestamp.now("UTC").isoformat(),
                    "cached": False,
                    "latency_ms": (time.monotonic() - t0) * 1000
                }
            )
            return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_holders(self, symbol: str, holder_type: str = "institutional") -> ProviderResult[HoldersResponse]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            df = ticker.institutional_holders if holder_type == "institutional" else ticker.mutualfund_holders
            items = []
            if df is not None and not df.empty:
                for _, r in df.iterrows():
                    items.append(HolderItem(
                        holder=str(r.get("Holder", "")),
                        shares=int(r.get("Shares")) if "Shares" in r and not pd.isna(r["Shares"]) else None,
                        date_reported=str(r.get("Date Reported")) if "Date Reported" in r and not pd.isna(r["Date Reported"]) else None,
                        percent_out=float(r.get("pctHeld")) if "pctHeld" in r and not pd.isna(r["pctHeld"]) else None,
                        value=float(r.get("Value")) if "Value" in r and not pd.isna(r["Value"]) else None
                    ))
            resp = HoldersResponse(
                symbol=symbol,
                type=holder_type,
                holders=items,
                metadata={
                    "source": self.name,
                    "retrieved_at": pd.Timestamp.now("UTC").isoformat(),
                    "cached": False,
                    "latency_ms": (time.monotonic() - t0) * 1000
                }
            )
            return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_insider_transactions(self, symbol: str) -> ProviderResult[InsiderTransactionsResponse]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            df = ticker.insider_transactions
            items = []
            if df is not None and not df.empty:
                for _, r in df.head(30).iterrows():
                    items.append(InsiderTransactionItem(
                        insider_name=str(r.get("Insider", r.get("Filer", ""))),
                        relation=str(r.get("Position", r.get("Relation", ""))) if not pd.isna(r.get("Position", r.get("Relation"))) else None,
                        transaction_date=str(r.get("Start Date", r.get("Date", ""))) if not pd.isna(r.get("Start Date", r.get("Date"))) else None,
                        transaction_type=str(r.get("Text", r.get("Transaction", ""))) if not pd.isna(r.get("Text", r.get("Transaction"))) else None,
                        shares=int(r.get("Shares")) if "Shares" in r and not pd.isna(r["Shares"]) else None,
                        value=float(r.get("Value")) if "Value" in r and not pd.isna(r["Value"]) else None
                    ))
            resp = InsiderTransactionsResponse(
                symbol=symbol,
                count=len(items),
                transactions=items,
                metadata={
                    "source": self.name,
                    "retrieved_at": pd.Timestamp.now("UTC").isoformat(),
                    "cached": False,
                    "latency_ms": (time.monotonic() - t0) * 1000
                }
            )
            return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def get_sustainability(self, symbol: str) -> ProviderResult[SustainabilityResponse]:
        t0 = time.monotonic()
        try:
            ticker = self._get_ticker(symbol)
            df = ticker.sustainability
            data_obj = None
            if df is not None and not df.empty:
                # df usually has index with metrics and a column 'Value'
                data_dict = {}
                for idx, r in df.iterrows():
                    val = r.iloc[0] if len(r) > 0 else None
                    data_dict[str(idx).lower()] = val

                data_obj = ESGRatingsData(
                    total_esg=float(data_dict.get("totalesg")) if "totalesg" in data_dict and data_dict["totalesg"] is not None else None,
                    environment_score=float(data_dict.get("environmentscore")) if "environmentscore" in data_dict and data_dict["environmentscore"] is not None else None,
                    social_score=float(data_dict.get("socialscore")) if "socialscore" in data_dict and data_dict["socialscore"] is not None else None,
                    governance_score=float(data_dict.get("governancescore")) if "governancescore" in data_dict and data_dict["governancescore"] is not None else None,
                    percentile=float(data_dict.get("percentile")) if "percentile" in data_dict and data_dict["percentile"] is not None else None,
                    esg_performance=str(data_dict.get("esgperformance")) if "esgperformance" in data_dict else None,
                    peer_group=str(data_dict.get("peergroup")) if "peergroup" in data_dict else None
                )

            resp = SustainabilityResponse(
                symbol=symbol,
                data=data_obj,
                metadata={
                    "source": self.name,
                    "retrieved_at": pd.Timestamp.now("UTC").isoformat(),
                    "cached": False,
                    "latency_ms": (time.monotonic() - t0) * 1000
                }
            )
            return ProviderResult(data=resp, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)
        except Exception as e:
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)
