# QuantSynthica API & Python SDK Documentation
**Domain**: `https://your-deployment-url.com` | **PyPI**: `quantsynthica 1.1.1` | **License**: Apache-2.0

---

## Table of Contents
1. [Overview & Architecture](#overview--architecture)
2. [Installation & Quickstart](#installation--quickstart)
3. [Python SDK Core Interfaces](#python-sdk-core-interfaces)
4. [Market Data API](#market-data-api)
5. [Financial Statements & Fundamentals](#financial-statements--fundamentals)
6. [Fundamental Ratios & Analyst Consensus](#fundamental-ratios--analyst-consensus)
7. [4-in-1 Institutional Valuation Models](#4-in-1-institutional-valuation-models)
8. [Modern Portfolio Theory (MPT) Optimization](#modern-portfolio-theory-mpt-optimization)
9. [Algorithmic Strategy Backtesting](#algorithmic-strategy-backtesting)
10. [Vectorized Technical Indicators](#vectorized-technical-indicators)
11. [Multi-Asset Screener (TradingView)](#multi-asset-screener-tradingview)
12. [Financial Sentiment & NLP Engine](#financial-sentiment--nlp-engine)
13. [Institutional Reports & Factsheets](#institutional-reports--factsheets)
14. [Real-time WebSockets Streaming](#real-time-websockets-streaming)
15. [REST API Endpoints Reference](#rest-api-endpoints-reference)

---

## Overview & Architecture

QuantSynthica provides a unified quantitative intelligence framework. It operates in two modes:

1. **Serverless Standalone Python Library (`import quantsynthica as qs`)**:
   - Zero-server, zero-API key, runs directly on Google Colab, Jupyter, or local machine.
   - Leverages client-side engines for local math computation (DCF, Piotroski, MPT, Backtesting, Indicators).
   - Zero infrastructure cost.
2. **High-Performance REST & WebSocket Microservice (`FastAPI`)**:
   - 53 endpoints with Redis caching, PostgreSQL/SQLite fallback, rate-limiting, and WebSocket tick streaming.
   - Deployed on Docker, Render, Railway, AWS, or local cluster.

---

## Installation & Quickstart

### Installation from PyPI
```bash
pip install --upgrade quantsynthica
```

### Installation in Google Colab
```python
!pip install --upgrade quantsynthica
import quantsynthica as qs

# Live quotes for Indian & US symbols
reliance = qs.get_quote("RELIANCE")
aapl = qs.get_quote("AAPL")
```

---

## Python SDK Core Interfaces

QuantSynthica provides three developer paradigms:

### 1. Top-Level Functional API (Quickest)
```python
import quantsynthica as qs

quote = qs.get_quote("RELIANCE")
valuation = qs.get_valuation("RELIANCE")
ratios = qs.get_ratios("RELIANCE")
portfolio = qs.optimize_portfolio(["RELIANCE", "TCS", "INFY"])
```

### 2. Object-Oriented `Ticker` / `Stock` API
```python
import quantsynthica as qs

stock = qs.Ticker("TCS")
q = stock.quote()
hist = stock.history(period="1y")
fin = stock.financials()
tech = stock.technicals()
dcf = stock.dcf(growth_rate=0.14)
```

### 3. Remote REST Client API (For Hosted Deployments)
```python
from quantsynthica import QuantSynthica

client = QuantSynthica(
    base_url="https://your-deployment-url.com",
    api_key="your_api_key" # optional
)
quote = client.market.get_quote("RELIANCE")
```

---

## Market Data API

### `qs.get_quote(symbol: str) -> DotDict`
Fetches real-time price, percentage change, day volume, market cap, and 52-week high/low.

**Parameters:**
- `symbol` *(str)*: Stock ticker symbol (e.g. `"RELIANCE"`, `"TCS"`, `"AAPL"`, `"NVDA"`). Indian tickers automatically resolve `.NS` (NSE) or `.BO` (BSE).

**Example Output:**
```python
quote = qs.get_quote("RELIANCE")
print(quote.symbol)             # "RELIANCE.NS"
print(quote.price)              # 1257.5
print(quote.change_percent)     # -0.85
print(quote.volume)             # 8492040
print(quote.market_cap)         # 17028912384000
print(quote.pe_ratio)           # 22.78
```

### `qs.get_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame`
Fetches historical OHLCV price bars.

**Parameters:**
- `period` *(str)*: Data range (`"1d"`, `"5d"`, `"1mo"`, `"3mo"`, `"6mo"`, `"1y"`, `"2y"`, `"5y"`, `"max"`).
- `interval` *(str)*: Bar frequency (`"1m"`, `"2m"`, `"5m"`, `"15m"`, `"1h"`, `"1d"`, `"1wk"`, `"1mo"`).

---

## Financial Statements & Fundamentals

### `qs.get_financials(symbol: str, quarterly: bool = False) -> pd.DataFrame`
Returns the complete multi-year or quarterly Income Statement as a pandas DataFrame.
- Rows include: `Total Revenue`, `Cost Of Revenue`, `Gross Profit`, `Operating Expense`, `Operating Income`, `Pretax Income`, `Net Income`, `EBIT`, `EBITDA`.

### `qs.get_balance_sheet(symbol: str, quarterly: bool = False) -> pd.DataFrame`
Returns the historical Balance Sheet statement.
- Rows include: `Total Assets`, `Current Assets`, `Cash And Cash Equivalents`, `Inventory`, `Total Liabilities Net Minority Interest`, `Current Liabilities`, `Total Debt`, `Stockholders Equity`, `Working Capital`.

### `qs.get_cashflow(symbol: str, quarterly: bool = False) -> pd.DataFrame`
Returns the Statement of Cash Flows.
- Rows include: `Operating Cash Flow`, `Capital Expenditure`, `Free Cash Flow`, `Investing Cash Flow`, `Financing Cash Flow`, `End Cash Position`.

---

## Fundamental Ratios & Analyst Consensus

### `qs.get_ratios(symbol: str) -> DotDict`
Calculates and normalizes institutional valuation, profitability, and solvency ratios.

**Response Fields:**
- `pe_trailing`: Trailing Price-to-Earnings ratio.
- `pe_forward`: Forward 1-year P/E projection.
- `price_to_book`: Market price relative to book value per share.
- `ev_to_ebitda`: Enterprise Value / EBITDA.
- `operating_margin_pct`: Operating profit margin (%).
- `net_margin_pct`: Net profit margin after tax (%).
- `return_on_equity_pct`: Return on Equity (ROE %).
- `debt_to_equity`: Total debt to shareholders' equity.
- `revenue_growth_pct`: Year-over-year revenue expansion rate.

### `qs.get_analyst_targets(symbol: str) -> DotDict`
Returns Wall Street and Dalal Street consensus price targets and institutional recommendations.
- `target_mean_price`: Consensus average 12-month target.
- `target_high_price`: Bull-case target.
- `target_low_price`: Bear-case target.
- `recommendation`: `"strong_buy"`, `"buy"`, `"hold"`, `"underperform"`, `"sell"`.
- `number_of_analysts`: Total institutional research analysts covering the stock.

### `qs.get_profile(symbol: str) -> DotDict`
Returns company overview, sector, industry classification, employee headcount, headquarters, website, and executive summary.

---

## 4-in-1 Institutional Valuation Models

### `qs.get_valuation(symbol: str) -> DotDict`
Computes all four mathematical valuation frameworks in a single call.

### 1. Discounted Cash Flow (DCF) Model
`stock.dcf(growth_rate, discount_rate=0.105, terminal_growth_rate=0.035, years=5)`
- **FCF Projections**: Projects future free cash flows discounted back to present value using WACC.
- **Terminal Value**: Calculated via Gordon Growth Perpetual Model or Exit Multiple.
- **Enterprise-to-Equity Bridge**: Net Debt deduction + Shares outstanding normalization.
- **Outputs**: `fair_value_per_share`, `upside_pct`, `margin_of_safety_pct`.

### 2. Piotroski 9-Point F-Score
`stock.piotroski()`
Evaluates financial strength on a 0–9 discrete accounting scale:
- **Profitability (4 pts)**: Positive ROA, Positive CFO, CFO > Net Income, Positive change in ROA.
- **Leverage & Liquidity (3 pts)**: Lower Long-Term Debt, Higher Current Ratio, No Share Dilution.
- **Operating Efficiency (2 pts)**: Higher Gross Margin, Higher Asset Turnover.
- **Rating**: `8-9`: Strong / High Quality | `4-7`: Stable | `0-3`: Weak / High Risk.

### 3. Altman Z-Score
`stock.altman_z()`
Assesses bankruptcy vulnerability:
$$Z = 1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 1.0X_5$$
- **Zones**:
  - `Safe Zone` ($Z > 2.99$): Minimal distress risk.
  - `Grey Zone` ($1.81 \le Z \le 2.99$): Moderate caution.
  - `Distress Zone` ($Z < 1.81$): Severe insolvency risk.

### 4. Benjamin Graham Number
`stock.graham()`
Calculates the classic value investing threshold:
$$\text{Graham Number} = \sqrt{22.5 \times \text{EPS} \times \text{BVPS}}$$

---

## Modern Portfolio Theory (MPT) Optimization

### `qs.optimize_portfolio(symbols: List[str], objective: str = "max_sharpe", period: str = "1y", risk_free_rate: float = 0.05) -> DotDict`

Uses the Scipy SLSQP quadratic programming solver to determine optimal asset allocation along the Markowitz Efficient Frontier.

**Objectives:**
- `"max_sharpe"`: Maximizes Sharpe Ratio ($\frac{R_p - R_f}{\sigma_p}$).
- `"min_volatility"`: Minimizes portfolio variance ($\sigma_p$).

**Outputs:**
- `optimal_portfolio.expected_annual_return_pct`: Annualized expected return.
- `optimal_portfolio.annual_volatility_pct`: Annualized standard deviation.
- `optimal_portfolio.sharpe_ratio`: Risk-adjusted excess return ratio.
- `allocations`: List of `{ "symbol": str, "weight_pct": float }`.

---

## Algorithmic Strategy Backtesting

### `qs.backtest(symbol: str, strategy: str = "sma_crossover", period: str = "2y", params: dict = None, initial_capital: float = 100000.0) -> DotDict`

Simulates trading strategies with realistic transaction costs and execution friction.

**Available Strategies:**
1. `"sma_crossover"`: `params={"fast_period": 10, "slow_period": 30}`
2. `"rsi_reversion"`: `params={"rsi_period": 14, "oversold": 30, "overbought": 70}`

**Performance Metrics:**
- `total_return_pct`: Cumulative strategy return.
- `total_trades`: Total completed buy/sell cycles.
- `win_rate_pct`: Percentage of profitable trades.
- `final_equity`: Ending portfolio equity.

---

## Vectorized Technical Indicators

### `qs.get_technicals(symbol: str, period: str = "1y") -> DotDict`
Computes key technical momentum and trend indicators:
- **Moving Averages**: `sma_20`, `sma_50`, `sma_200`, `ema_20`, `ema_50`.
- **RSI**: 14-period Relative Strength Index.
- **MACD**: MACD Line, Signal Line (9-day EMA), MACD Histogram.
- **Bollinger Bands**: Upper Band, Middle Band (20 SMA), Lower Band, Bandwidth.

---

## Multi-Asset Screener (TradingView)

### `qs.screener.value_stocks(market: str = "india", limit: int = 50) -> DotDict`
Screens for undervalued, high-earning stocks ($0 < \text{P/E} < 25$, Market Cap $> 1\text{B}$).

### `qs.screener.growth_stocks(market: str = "india", limit: int = 50) -> DotDict`
Screens for high earnings and revenue growth stocks.

### `qs.screener.crypto(limit: int = 50) -> DotDict`
Screens top cryptocurrencies across major exchanges sorted by 24h trading volume.

### `qs.screener.forex(limit: int = 50) -> DotDict`
Screens major and minor currency pairs.

---

## Financial Sentiment & NLP Engine

### `qs.get_sentiment(symbol_or_text: str) -> DotDict`
Dual-mode financial sentiment analyzer:
1. **Ticker Symbol** (`"TCS"`): Scrapes latest news headlines, computes compound sentiment, and classifies as `Bullish`, `Bearish`, or `Neutral`.
2. **Financial Headline / Text**: Analyzes arbitrary commentary using a financial lexicon (`"surge"`, `"plunge"`, `"beat"`, `"guidance"`).

---

## Institutional Reports & Factsheets

Available via the REST API microservice:
- `GET /api/v1/reports/excel/{symbol}`: Downloads a 3-tab formatted institutional Excel workbook (`.xlsx`) with `Company Overview`, `Valuation Models`, and `Historical Bars`.
- `GET /api/v1/reports/tearsheet/{symbol}`: Returns a clean, printable HTML one-page institutional tearsheet.

---

## Real-time WebSockets Streaming

### `WebSocket /api/v1/ws/quotes`
Bidirectional JSON protocol for tick updates:

**Client Subscribe:**
```json
{ "action": "subscribe", "symbols": ["RELIANCE", "TCS", "AAPL"] }
```

**Server Tick Broadcast:**
```json
{
  "type": "quote",
  "symbol": "RELIANCE.NS",
  "price": 1258.10,
  "change_percent": -0.80,
  "timestamp": "2026-09-13T16:20:00Z"
}
```

---

## REST API Endpoints Reference

Base URL: `https://your-deployment-url.com/api/v1`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health and provider diagnostic |
| `GET` | `/search?q={query}` | Search and resolve ticker symbols |
| `GET` | `/market/{symbol}/quote` | Real-time market quote |
| `GET` | `/market/{symbol}/history` | Historical OHLCV bar series |
| `GET` | `/fundamentals/{symbol}/income-statement` | Multi-year income statement |
| `GET` | `/fundamentals/{symbol}/balance-sheet` | Multi-year balance sheet |
| `GET` | `/fundamentals/{symbol}/cash-flow` | Multi-year cash flows |
| `GET` | `/fundamentals/{symbol}/ratios` | Key financial and valuation ratios |
| `GET` | `/valuation/{symbol}` | 4-in-1 institutional valuation |
| `POST` | `/valuation/dcf` | Custom parameter DCF calculation |
| `POST` | `/portfolio/optimize` | Markowitz MPT portfolio optimization |
| `POST` | `/portfolio/backtest` | Algorithmic strategy backtesting |
| `POST` | `/screener/stocks` | TradingView stock screening |
| `POST` | `/screener/crypto` | TradingView cryptocurrency screening |
| `GET` | `/sentiment/{symbol}` | Aggregated news sentiment score |
| `POST` | `/sentiment/analyze` | Ad-hoc text sentiment analysis |
| `GET` | `/reports/excel/{symbol}` | Generate institutional Excel report |
| `GET` | `/reports/tearsheet/{symbol}` | Generate printable HTML tearsheet |
| `WS` | `/ws/quotes` | Streaming live price tick socket |
