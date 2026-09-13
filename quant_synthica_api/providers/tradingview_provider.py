import sys
import time
from typing import Optional, Dict, Any, List
import pandas as pd

from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.logging import logger
from quant_synthica_api.providers.base import BaseProvider, ProviderResult
from quant_synthica_api.schemas.screener import (
    ScreenerQueryRequest, ScreenerFilter, ScreenerStockItem, ScreenerResponse,
    GenericScreenerRequest, MultiAssetItem, MultiAssetScreenerResponse
)

# Ensure local TradingView-Screener repository is imported safely
settings = get_settings()
tv_path_str = str(settings.TRADINGVIEW_DIR)
if tv_path_str not in sys.path:
    sys.path.insert(0, tv_path_str)

try:
    from tradingview_screener import (
        Query, col, stocks, crypto, coin, crypto_dex, forex, futures, bond, cfd
    )
    HAS_TRADINGVIEW = True
except Exception as e:
    logger.error(f"Failed to import tradingview_screener: {e}")
    HAS_TRADINGVIEW = False

class TradingViewProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="tradingview")

    def health_check(self) -> bool:
        return HAS_TRADINGVIEW

    def query_screener(self, req: ScreenerQueryRequest) -> ProviderResult[ScreenerResponse]:
        t0 = time.monotonic()
        if not HAS_TRADINGVIEW:
            return ProviderResult(
                data=None, provider=self.name, success=False, error="tradingview_screener not loaded", latency_ms=(time.monotonic() - t0) * 1000
            )

        try:
            market = req.market.lower()
            q = stocks(market)

            # Custom or default columns
            if req.select_columns:
                columns = req.select_columns
                # Ensure name/ticker included
                for base_col in ["name", "description", "close", "change"]:
                    if base_col not in columns:
                        columns.append(base_col)
            else:
                columns = [
                    "name", "description", "close", "change", "volume",
                    "market_cap_basic", "price_earnings_ttm", "price_book_ratio",
                    "return_on_equity", "sector", "AnalystRating"
                ]
            q = q.select(*columns)

            conditions = []
            f = req.filters or ScreenerFilter()

            # Exchange filtering
            if req.exchange:
                conditions.append(col("exchange") == req.exchange.upper())

            # Filter conditions
            if f.market_cap_min is not None:
                conditions.append(col("market_cap_basic") >= f.market_cap_min)
            if f.market_cap_max is not None:
                conditions.append(col("market_cap_basic") <= f.market_cap_max)
            if f.pe_min is not None:
                conditions.append(col("price_earnings_ttm") >= f.pe_min)
            if f.pe_max is not None:
                conditions.append(col("price_earnings_ttm") <= f.pe_max)
            if f.pb_max is not None:
                conditions.append(col("price_book_ratio") <= f.pb_max)
            if f.roe_min is not None:
                conditions.append(col("return_on_equity") >= f.roe_min)
            if f.dividend_yield_min is not None:
                conditions.append(col("dividend_yield_recent") >= f.dividend_yield_min)
            if f.volume_min is not None:
                conditions.append(col("volume") >= f.volume_min)
            if f.rsi_min is not None:
                conditions.append(col("RSI") >= f.rsi_min)
            if f.rsi_max is not None:
                conditions.append(col("RSI") <= f.rsi_max)
            if f.sector:
                conditions.append(col("sector") == f.sector)

            if conditions:
                q = q.where(*conditions)

            # Sorting
            sort_by = req.sort_by or "market_cap_basic"
            sort_asc = (req.sort_order.lower() == "asc") if req.sort_order else False
            q = q.order_by(sort_by, ascending=sort_asc)

            # Pagination
            q = q.offset(req.offset).limit(req.limit)

            total_count, df = q.get_scanner_data()

            items: List[ScreenerStockItem] = []
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    ticker_str = str(row.get("ticker", ""))
                    name_str = str(row.get("name", ""))
                    symbol_str = ticker_str.split(":")[-1] if ":" in ticker_str else name_str
                    exchange_str = ticker_str.split(":")[0] if ":" in ticker_str else req.exchange

                    price_val = float(row["close"]) if "close" in row and not pd.isna(row["close"]) else None
                    chg_val = float(row["change"]) if "change" in row and not pd.isna(row["change"]) else None
                    vol_val = float(row["volume"]) if "volume" in row and not pd.isna(row["volume"]) else None
                    mcap_val = float(row["market_cap_basic"]) if "market_cap_basic" in row and not pd.isna(row["market_cap_basic"]) else None
                    pe_val = float(row["price_earnings_ttm"]) if "price_earnings_ttm" in row and not pd.isna(row["price_earnings_ttm"]) else None
                    pb_val = float(row["price_book_ratio"]) if "price_book_ratio" in row and not pd.isna(row["price_book_ratio"]) else None
                    roe_val = float(row["return_on_equity"]) if "return_on_equity" in row and not pd.isna(row["return_on_equity"]) else None
                    sector_val = str(row.get("sector")) if not pd.isna(row.get("sector")) else None
                    rating_val = str(row.get("AnalystRating")) if not pd.isna(row.get("AnalystRating")) else None
                    desc_val = str(row.get("description")) if not pd.isna(row.get("description")) else name_str

                    # Capture any extra requested fields
                    known_cols = {"ticker", "name", "description", "close", "change", "volume", "market_cap_basic", "price_earnings_ttm", "price_book_ratio", "return_on_equity", "sector", "AnalystRating"}
                    extra_dict = {}
                    for c in df.columns:
                        if c not in known_cols and not pd.isna(row[c]):
                            extra_dict[c] = row[c]

                    items.append(ScreenerStockItem(
                        ticker=ticker_str,
                        symbol=symbol_str,
                        name=desc_val or name_str,
                        exchange=exchange_str,
                        price=price_val,
                        change_percent=chg_val,
                        volume=vol_val,
                        market_cap=mcap_val,
                        pe_ratio=pe_val,
                        pb_ratio=pb_val,
                        roe=roe_val,
                        sector=sector_val,
                        rating=rating_val,
                        extra_fields=extra_dict if extra_dict else None
                    ))

            response_data = ScreenerResponse(
                total_count=int(total_count) if total_count is not None else len(items),
                count=len(items),
                items=items,
                metadata={
                    "source": self.name,
                    "retrieved_at": pd.Timestamp.now("UTC").isoformat(),
                    "cached": False,
                    "latency_ms": (time.monotonic() - t0) * 1000
                }
            )

            return ProviderResult(data=response_data, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)

        except Exception as e:
            logger.error(f"TradingView query_screener failed: {e}")
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)

    def query_multi_asset(self, asset_class: str, req: GenericScreenerRequest) -> ProviderResult[MultiAssetScreenerResponse]:
        t0 = time.monotonic()
        if not HAS_TRADINGVIEW:
            return ProviderResult(data=None, provider=self.name, success=False, error="tradingview_screener not loaded", latency_ms=(time.monotonic() - t0) * 1000)

        try:
            asset_clean = asset_class.lower().strip()
            if asset_clean == "crypto":
                q = crypto()
            elif asset_clean == "coin":
                q = coin()
            elif asset_clean == "crypto_dex":
                q = crypto_dex()
            elif asset_clean == "forex":
                q = forex()
            elif asset_clean == "futures":
                q = futures()
            elif asset_clean == "bond" or asset_clean == "bonds":
                q = bond()
            elif asset_clean == "cfd":
                q = cfd()
            else:
                return ProviderResult(data=None, provider=self.name, success=False, error=f"Unsupported asset class: {asset_class}", latency_ms=(time.monotonic() - t0) * 1000)

            if req.select_columns:
                q = q.select(*req.select_columns)

            if req.sort_by:
                sort_asc = (req.sort_order.lower() == "asc") if req.sort_order else False
                q = q.order_by(req.sort_by, ascending=sort_asc)

            q = q.offset(req.offset).limit(req.limit)

            total_count, df = q.get_scanner_data()

            items: List[MultiAssetItem] = []
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    ticker_str = str(row.get("ticker", row.get("ticker-view", row.get("name", ""))))
                    name_str = str(row.get("name", row.get("description", ticker_str)))
                    price_val = float(row["close"]) if "close" in row and not pd.isna(row["close"]) else None
                    chg_val = float(row.get("24h_close_change|5", row.get("change", 0.0))) if not pd.isna(row.get("24h_close_change|5", row.get("change", 0.0))) else None
                    vol_val = float(row.get("24h_vol|5", row.get("volume", 0.0))) if not pd.isna(row.get("24h_vol|5", row.get("volume", 0.0))) else None

                    extra_data = {}
                    for col_name in df.columns:
                        if col_name not in ["ticker", "name", "close", "change"]:
                            val = row[col_name]
                            if isinstance(val, (list, tuple, dict)):
                                extra_data[col_name] = val
                            elif hasattr(val, "__len__") and not isinstance(val, str):
                                extra_data[col_name] = list(val)
                            elif pd.notna(val):
                                extra_data[col_name] = val.item() if hasattr(val, "item") else val


                    items.append(MultiAssetItem(
                        ticker=ticker_str,
                        name=name_str,
                        price=price_val,
                        change=chg_val,
                        volume=vol_val,
                        extra_fields=extra_data
                    ))

            response_data = MultiAssetScreenerResponse(
                asset_class=asset_clean,
                total_count=int(total_count) if total_count is not None else len(items),
                count=len(items),
                items=items,
                metadata={
                    "source": self.name,
                    "retrieved_at": pd.Timestamp.now("UTC").isoformat(),
                    "cached": False,
                    "latency_ms": (time.monotonic() - t0) * 1000
                }
            )

            return ProviderResult(data=response_data, provider=self.name, success=True, latency_ms=(time.monotonic() - t0) * 1000)

        except Exception as e:
            logger.error(f"TradingView query_multi_asset failed for {asset_class}: {e}")
            return ProviderResult(data=None, provider=self.name, success=False, error=str(e), latency_ms=(time.monotonic() - t0) * 1000)
