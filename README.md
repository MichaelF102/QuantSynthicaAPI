# QuantSynthica Market API & Python Library

[![PyPI version](https://img.shields.io/pypi/v/quantsynthica.svg)](https://pypi.org/project/quantsynthica/)
[![Python Version](https://img.shields.io/pypi/pyversions/quantsynthica.svg)](https://pypi.org/project/quantsynthica/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI Tests](https://github.com/MichaelF102/QuantSynthicaAPI/actions/workflows/test.yml/badge.svg)](https://github.com/MichaelF102/QuantSynthicaAPI/actions/workflows/test.yml)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MichaelF102/QuantSynthicaAPI/blob/main/notebooks/quantsynthica_colab_demo.ipynb)

**QuantSynthica** is a unified quantitative financial engine combining `yfinance`, `TradingView-Screener`, `Screener.in`, Modern Portfolio Theory, DCF valuation, algorithmic backtesting, and sentiment analysis into a single canonical interface.

### ⚡ Use Instantly in Python (Zero Server Required, Free Forever Like `yfinance`)

```bash
pip install quantsynthica
```

```python
import quantsynthica as qs

# Live quotes (Indian & US stocks)
quote = qs.get_quote("RELIANCE")

# 4-in-1 Valuation Models (DCF, Piotroski, Altman Z, Graham Number)
val = qs.get_valuation("RELIANCE")

# Markowitz Efficient Frontier Portfolio Optimization
opt = qs.optimize_portfolio(["RELIANCE", "TCS", "INFY"])

# TradingView multi-asset screener
screener_results = qs.screener.value_stocks(market="india")
```

---


## Third-Party Components & Attribution

This API is an independent project that builds on and wraps existing open-source components without modifying their upstream source code:

- **yfinance** ([https://github.com/ranaroussi/yfinance](https://github.com/ranaroussi/yfinance))
  - License: Apache License 2.0
  - Copyright: 2017-2024 Ran Aroussi
  - Usage: Wrapped via `quant_synthica_api/providers/yfinance_provider.py` for market quotes, historical bars, dividends, options, analyst recommendations, and statements.
- **TradingView-Screener** ([https://github.com/shner-elmo/TradingView-Screener](https://github.com/shner-elmo/TradingView-Screener))
  - License: MIT License
  - Copyright: 2023-2024 shner-elmo
  - Usage: Wrapped via `quant_synthica_api/providers/tradingview_provider.py` for multi-asset screening across Stocks, Crypto, Forex, Futures, Bonds, and CFDs.
- **BeautifulSoup4** (MIT License / Python Software Foundation License)
  - Usage: Utilized in `quant_synthica_api/providers/screener_provider.py` to parse publicly available corporate filings, peer comparisons, and statements from Screener.in.

---

## Architecture Overview

```
QuantSynthica API
       │
    FastAPI (Authentication, Rate-Limiting, OpenAPI Docs)
       │
   API Services Layer (Market, Fundamentals, Screener, Technical, Quant, Stock Profile)
       │
   Normalization & Fallback Layer (Canonical Schemas, Provider Hierarchy, Source Attribution)
       │
 ┌───────────────────────┼───────────────────────┐
 │                       │                       │
yfinance Provider    TradingView Provider    Screener.in Provider
(Local Repo Wrapper) (Local Repo Wrapper)    (BS4 Scraper + Rate Throttling)
 │                       │                       │
 └───────────────────────┼───────────────────────┘
                         │
        Cache & Persistence Storage Layer
              ┌──────────┴──────────┐
              │                     │
         Redis Cache            PostgreSQL
     (with memory fallback) (SQLAlchemy + Alembic)
```

---

## Complete List of API Endpoints (53 Endpoints)

### 1. Market Data (`/api/v1/market`)
- `GET /api/v1/market/{symbol}/quote` — Real-time or latest market quote
- `GET /api/v1/market/{symbol}/history?period=1y&interval=1d` — Historical OHLCV bars
- `GET /api/v1/market/{symbol}/dividends` — Historical dividend distributions
- `GET /api/v1/market/{symbol}/splits` — Stock split records
- `GET /api/v1/market/{symbol}/recommendations` — Analyst consensus recommendations & target prices *(yfinance)*
- `GET /api/v1/market/{symbol}/upgrades-downgrades` — Historical rating changes from Wall Street firms *(yfinance)*
- `GET /api/v1/market/{symbol}/options` — Complete option chain with Calls & Puts *(yfinance)*
- `GET /api/v1/market/{symbol}/news` — Real-time company news feed *(yfinance)*

### 2. Fundamentals (`/api/v1/fundamentals`)
- `GET /api/v1/fundamentals/{symbol}` — Unified fundamental profile
- `GET /api/v1/fundamentals/{symbol}/income-statement` — Annual/Quarterly income statement / P&L
- `GET /api/v1/fundamentals/{symbol}/balance-sheet` — Balance sheet statement
- `GET /api/v1/fundamentals/{symbol}/cash-flow` — Cash flow statement
- `GET /api/v1/fundamentals/{symbol}/ratios` — Valuation ratios (P/E, P/B, ROCE, ROE, Debt/Equity)
- `GET /api/v1/fundamentals/{symbol}/shareholding` — Shareholding pattern across promoters, FIIs, DIIs, public
- `GET /api/v1/fundamentals/{symbol}/institutional-holders` — Top institutional shareholders *(yfinance)*
- `GET /api/v1/fundamentals/{symbol}/mutual-funds` — Mutual fund shareholders *(yfinance)*
- `GET /api/v1/fundamentals/{symbol}/insider-transactions` — Insider buy/sell transactions *(yfinance)*
- `GET /api/v1/fundamentals/{symbol}/sustainability` — ESG and sustainability risk ratings *(yfinance)*
- `GET /api/v1/fundamentals/{symbol}/peers` — Industry peer comparison table *(Screener.in)*
- `GET /api/v1/fundamentals/{symbol}/analysis` — Pros and cons corporate analysis *(Screener.in)*
- `GET /api/v1/fundamentals/{symbol}/documents` — Concall transcripts, presentations, annual reports *(Screener.in)*

### 3. Multi-Asset Screener (`/api/v1/screener`) *(TradingView)*
- `POST /api/v1/screener/query` — Stock screener with custom 3000+ column support and SQL-like filters
- `GET /api/v1/screener/value` — Predefined screen: Value stocks
- `GET /api/v1/screener/growth` — Predefined screen: High Growth stocks
- `GET /api/v1/screener/momentum` — Predefined screen: Momentum stocks
- `GET /api/v1/screener/dividend` — Predefined screen: High Dividend Yield stocks
- `POST /api/v1/screener/crypto` — Centralized crypto pairs (CEX) screener
- `POST /api/v1/screener/coin` — CoinMarketCap coin rank screener
- `POST /api/v1/screener/forex` — Foreign exchange pairs screener
- `POST /api/v1/screener/futures` — Commodity & Index futures screener
- `POST /api/v1/screener/bonds` — Sovereign & Corporate bonds screener
- `POST /api/v1/screener/cfd` — Contract for Difference (CFD) screener

### 4. Technical Analysis (`/api/v1/technical`)
- `GET /api/v1/technical/{symbol}?period=1y` — Full technical indicator suite (SMA 20/50/200, EMA 12/26, RSI 14, MACD, Bollinger Bands, ATR 14, ADX 14, VWAP)

### 5. Quantitative Analytics (`/api/v1/quant`)
- `GET /api/v1/quant/{symbol}/returns` — Daily return, cumulative return, CAGR, 1M/3M/6M/12M momentum
- `GET /api/v1/quant/{symbol}/risk` — Annualized volatility, Sharpe ratio, Sortino ratio, Max Drawdown, VaR 95%, CVaR 95%, Beta, Alpha
- `GET /api/v1/quant/{symbol}/volatility` — Volatility metrics (daily, annualized, 20d rolling, Parkinson volatility, ATR)
- `GET /api/v1/quant/{symbol}/summary` — Combined Quant Summary (Returns + Risk + Technicals)

### 6. Valuation Models (`/api/v1/valuation`)
- `GET /api/v1/valuation/{symbol}` — Comprehensive valuation overview combining DCF, Piotroski F-Score, Altman Z-Score, and Graham Number
- `POST /api/v1/valuation/dcf` — Configurable Discounted Cash Flow (DCF) model with custom growth rates, WACC discount rate, and terminal value assumptions
- `GET /api/v1/valuation/piotroski/{symbol}` — Piotroski 9-point fundamental financial health score and itemized criteria breakdown
- `GET /api/v1/valuation/altman-z/{symbol}` — Altman Z-Score for bankruptcy distress prediction and credit zone classification
- `GET /api/v1/valuation/graham/{symbol}` — Benjamin Graham Number & Net-Net Working Capital valuation

### 7. Portfolio Optimization & Strategy Backtesting (`/api/v1/portfolio`)
- `POST /api/v1/portfolio/optimize` — Markowitz Modern Portfolio Theory (MPT) optimization (Max Sharpe, Min Volatility, Efficient Frontier)
- `POST /api/v1/portfolio/analytics` — Multi-asset correlation matrix, covariance matrix, joint portfolio volatility and VaR
- `POST /api/v1/portfolio/backtest` — Event-driven technical strategy backtesting (SMA/EMA Crossover, RSI Reversion, MACD, Bollinger Bands) with complete trade log, Sharpe, Max Drawdown, and Equity Curve

### 8. Financial Sentiment & NLP (`/api/v1/sentiment`)
- `GET /api/v1/sentiment/{symbol}` — Aggregate news sentiment index and article-level polarity breakdowns
- `POST /api/v1/sentiment/analyze` — Financial text sentiment analyzer augmented with domain-specific market lexicon

### 9. Institutional Reports & Exports (`/api/v1/reports`)
- `GET /api/v1/reports/excel/{symbol}` — Institutional multi-sheet Excel financial model workbook (`.xlsx`)
- `GET /api/v1/reports/tearsheet/{symbol}` — Printable institutional HTML/CSS factsheet tearsheet

### 10. Live WebSockets Streaming (`/api/v1/ws`)
- `WebSocket /api/v1/ws/quotes` — Real-time live quotes and tick streaming with subscription protocol (`subscribe`, `unsubscribe`, `ping`/`pong`)

### 11. Stock Profile & Search (`/api/v1`)
- `GET /api/v1/stocks/{symbol}` — 360° Unified Stock Profile combining Identity, Market, Valuation, Profitability, Growth, Technical, Quant, and multi-source provenance
- `GET /api/v1/health` — Provider health check, cache type, and system status
- `GET /api/v1/search?q={query}` — Central symbol resolver and fuzzy ticker search

---

## Installation & Setup

```bash
git clone https://github.com/MichaelF102/QuantSynthicaAPI.git
cd QuantSynthicaAPI

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize DB tables and seed known stock mappings
python -m quant_synthica_api.database.init_db
python scripts/seed_db.py

# Run development server
./scripts/run_dev.sh
```

API is available at: `http://localhost:8000`  
Swagger UI documentation: `http://localhost:8000/docs`

---

## Authentication & Security

- **Zero-Server SDK Mode**: No API key or server required (`import quantsynthica as qs`).
- **REST Microservice Mode**:
  - **Header Format**: Pass your key via the `X-API-Key` header:
    ```bash
    curl -H "X-API-Key: your_api_key" http://localhost:8000/api/v1/market/RELIANCE/quote
    ```
  - **Local Dev vs Production**: Authentication is **disabled by default** (`API_KEY_REQUIRED=False` in `.env`). To enforce API keys in production, set `API_KEY_REQUIRED=True` and define `API_KEY=your_secret_key` in your environment.

---

## Testing

Run all 61 automated unit and integration tests:

```bash
pytest tests/ -v
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for full release history and version notes.
