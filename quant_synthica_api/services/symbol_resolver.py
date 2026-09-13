import re
from typing import Optional, Dict
from quant_synthica_api.schemas.common import ResolvedSymbol
from quant_synthica_api.core.exceptions import SymbolResolutionError

# Well-known mappings for Indian equities (including BSE security codes)
KNOWN_MAPPINGS: Dict[str, Dict[str, str]] = {
    "RELIANCE": {"nse": "RELIANCE", "bse": "500325", "screener": "RELIANCE", "name": "Reliance Industries Ltd", "country": "IN"},
    "TCS": {"nse": "TCS", "bse": "532540", "screener": "TCS", "name": "Tata Consultancy Services Ltd", "country": "IN"},
    "INFY": {"nse": "INFY", "bse": "500209", "screener": "INFY", "name": "Infosys Ltd", "country": "IN"},
    "HDFCBANK": {"nse": "HDFCBANK", "bse": "500180", "screener": "HDFCBANK", "name": "HDFC Bank Ltd", "country": "IN"},
    "ICICIBANK": {"nse": "ICICIBANK", "bse": "532174", "screener": "ICICIBANK", "name": "ICICI Bank Ltd", "country": "IN"},
    "SBIN": {"nse": "SBIN", "bse": "500112", "screener": "SBIN", "name": "State Bank of India", "country": "IN"},
    "BHARTIARTL": {"nse": "BHARTIARTL", "bse": "532454", "screener": "BHARTIARTL", "name": "Bharti Airtel Ltd", "country": "IN"},
    "ITC": {"nse": "ITC", "bse": "500875", "screener": "ITC", "name": "ITC Ltd", "country": "IN"},
    "LT": {"nse": "LT", "bse": "500510", "screener": "LT", "name": "Larsen & Toubro Ltd", "country": "IN"},
    "HINDUNILVR": {"nse": "HINDUNILVR", "bse": "500696", "screener": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "country": "IN"},
    "TATAMOTORS": {"nse": "TATAMOTORS", "bse": "500570", "screener": "TATAMOTORS", "name": "Tata Motors Ltd", "country": "IN"},
    "WIPRO": {"nse": "WIPRO", "bse": "507685", "screener": "WIPRO", "name": "Wipro Ltd", "country": "IN"},
    "AAPL": {"canonical": "AAPL", "symbol": "AAPL", "exchange": "NASDAQ", "country": "US", "name": "Apple Inc."},
    "MSFT": {"canonical": "MSFT", "symbol": "MSFT", "exchange": "NASDAQ", "country": "US", "name": "Microsoft Corp."},
    "GOOGL": {"canonical": "GOOGL", "symbol": "GOOGL", "exchange": "NASDAQ", "country": "US", "name": "Alphabet Inc."},
    "AMZN": {"canonical": "AMZN", "symbol": "AMZN", "exchange": "NASDAQ", "country": "US", "name": "Amazon.com Inc."},
    "NVDA": {"canonical": "NVDA", "symbol": "NVDA", "exchange": "NASDAQ", "country": "US", "name": "NVIDIA Corp."},
    "TSLA": {"canonical": "TSLA", "symbol": "TSLA", "exchange": "NASDAQ", "country": "US", "name": "Tesla Inc."},
    "SPY": {"canonical": "SPY", "symbol": "SPY", "exchange": "AMEX", "country": "US", "name": "SPDR S&P 500 ETF"},
}


# Reverse mapping for BSE numerical codes to NSE symbol
BSE_CODE_TO_NSE: Dict[str, str] = {
    details["bse"]: sym for sym, details in KNOWN_MAPPINGS.items() if "bse" in details
}

class SymbolResolver:
    @staticmethod
    def resolve(symbol_input: str) -> ResolvedSymbol:
        if not symbol_input or not symbol_input.strip():
            raise SymbolResolutionError("Symbol input cannot be empty")

        clean = symbol_input.strip().upper()
        
        # Check if input is a known BSE numerical security code
        if clean.isdigit():
            if clean in BSE_CODE_TO_NSE:
                clean = BSE_CODE_TO_NSE[clean]
            else:
                # Numerical symbol for BSE
                return ResolvedSymbol(
                    input=symbol_input,
                    canonical=f"{clean}.BO",
                    symbol=clean,
                    exchange="BSE",
                    bse=clean,
                    tradingview=f"BSE:{clean}",
                    screener=clean,
                    yfinance=f"{clean}.BO",
                    country="IN"
                )

        # Detect suffix: .NS (NSE) or .BO (BSE)
        is_nse = clean.endswith(".NS")
        is_bse = clean.endswith(".BO")
        
        # Strip exchange prefix (e.g. NSE:RELIANCE or NASDAQ:AAPL)
        if ":" in clean:
            prefix, bare = clean.split(":", 1)
            prefix = prefix.strip()
            bare = bare.strip()
            if prefix in ("NSE", "BSE"):
                is_nse = (prefix == "NSE")
                is_bse = (prefix == "BSE")
                base = bare
            else:
                # US or other international exchange
                return ResolvedSymbol(
                    input=symbol_input,
                    canonical=bare,
                    symbol=bare,
                    exchange=prefix,
                    tradingview=f"{prefix}:{bare}",
                    yfinance=bare,
                    country="US"
                )
        else:
            base = clean.replace(".NS", "").replace(".BO", "")

        # Check in known mappings
        if base in KNOWN_MAPPINGS:
            info = KNOWN_MAPPINGS[base]
            if info.get("country") == "US":
                return ResolvedSymbol(
                    input=symbol_input,
                    canonical=info.get("canonical", base),
                    symbol=info.get("symbol", base),
                    exchange=info.get("exchange", "NASDAQ"),
                    tradingview=f"{info.get('exchange', 'NASDAQ')}:{base}",
                    yfinance=info.get("canonical", base),
                    country="US"
                )
            canonical = f"{info['nse']}.BO" if is_bse else f"{info['nse']}.NS"
            exchange = "BSE" if is_bse else "NSE"
            return ResolvedSymbol(
                input=symbol_input,
                canonical=canonical,
                symbol=info["nse"],
                exchange=exchange,
                nse=info["nse"],
                bse=info.get("bse"),
                tradingview=f"{exchange}:{info['nse']}",
                screener=info.get("screener", info["nse"]),
                yfinance=canonical,
                country=info.get("country", "IN")
            )


        # Heuristic resolution for Indian market vs US market
        # If user explicitly entered .NS or .BO or bare symbol assumed Indian
        if is_bse:
            canonical = f"{base}.BO"
            exchange = "BSE"
            tv_sym = f"BSE:{base}"
        else:
            # Default to NSE for Indian equity tickers
            canonical = f"{base}.NS"
            exchange = "NSE"
            tv_sym = f"NSE:{base}"

        return ResolvedSymbol(
            input=symbol_input,
            canonical=canonical,
            symbol=base,
            exchange=exchange,
            nse=base if exchange == "NSE" else None,
            bse=base if exchange == "BSE" else None,
            tradingview=tv_sym,
            screener=base,
            yfinance=canonical,
            country="IN"
        )
