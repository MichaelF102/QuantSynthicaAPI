"""Symbol resolution for local provider queries."""

from typing import NamedTuple, Optional
import re

class ResolvedSymbol(NamedTuple):
    original: str
    symbol: str
    canonical: str
    exchange: str
    country: str
    is_bse: bool = False
    is_nse: bool = False
    is_us: bool = False

KNOWN_MAPPINGS = {
    "500325": ("RELIANCE", "BSE"),
    "532540": ("TCS", "BSE"),
    "500209": ("INFY", "BSE"),
    "500180": ("HDFCBANK", "BSE"),
    "532174": ("ICICIBANK", "BSE"),
    "AAPL": ("AAPL", "NASDAQ"),
    "MSFT": ("MSFT", "NASDAQ"),
    "GOOGL": ("GOOGL", "NASDAQ"),
    "AMZN": ("AMZN", "NASDAQ"),
    "TSLA": ("TSLA", "NASDAQ"),
    "NVDA": ("NVDA", "NASDAQ"),
    "META": ("META", "NASDAQ"),
}

US_TICKERS = {"AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "NVDA", "META", "SPY", "QQQ"}


def resolve_symbol(raw_symbol: str) -> ResolvedSymbol:
    s = raw_symbol.strip().upper()
    if not s:
        raise ValueError("Symbol cannot be empty.")

    if s in KNOWN_MAPPINGS and KNOWN_MAPPINGS[s][1] != "BSE":
        return ResolvedSymbol(
            original=raw_symbol,
            symbol=s,
            canonical=s,
            exchange=KNOWN_MAPPINGS[s][1],
            country="US",
            is_us=True
        )

    if s.endswith(".NS"):
        base = s[:-3]
        return ResolvedSymbol(original=raw_symbol, symbol=base, canonical=s, exchange="NSE", country="IN", is_nse=True)
    if s.endswith(".BO"):
        base = s[:-3]
        return ResolvedSymbol(original=raw_symbol, symbol=base, canonical=s, exchange="BSE", country="IN", is_bse=True)
    if s.startswith("NSE:"):
        base = s[4:]
        return ResolvedSymbol(original=raw_symbol, symbol=base, canonical=f"{base}.NS", exchange="NSE", country="IN", is_nse=True)
    if s.startswith("BSE:"):
        base = s[4:]
        return ResolvedSymbol(original=raw_symbol, symbol=base, canonical=f"{base}.BO", exchange="BSE", country="IN", is_bse=True)

    if s.isdigit():
        mapped_name, _ = KNOWN_MAPPINGS.get(s, (s, "BSE"))
        return ResolvedSymbol(original=raw_symbol, symbol=mapped_name, canonical=f"{s}.BO", exchange="BSE", country="IN", is_bse=True)

    if s in US_TICKERS:
        return ResolvedSymbol(original=raw_symbol, symbol=s, canonical=s, exchange="US", country="US", is_us=True)

    # Default Indian stock to NSE
    return ResolvedSymbol(original=raw_symbol, symbol=s, canonical=f"{s}.NS", exchange="NSE", country="IN", is_nse=True)
