# QuantSynthica Python SDK

[![PyPI version](https://img.shields.io/pypi/v/quantsynthica.svg)](https://pypi.org/project/quantsynthica/)
[![Python Version](https://img.shields.io/pypi/pyversions/quantsynthica.svg)](https://pypi.org/project/quantsynthica/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MichaelF102/QuantSynthicaAPI/blob/main/notebooks/quantsynthica_colab_demo.ipynb)

The official Python client for **QuantSynthica Market API** — the unified financial data & quantitative engine combining `yfinance`, `TradingView-Screener`, `Screener.in`, Modern Portfolio Theory, DCF valuation, algorithmic backtesting, and sentiment analysis.

---

## Installation

```bash
pip install quantsynthica
```

---

## Quickstart (Zero-Server, 100% Free - Like `yfinance`)

No server, API key, or setup required. Run directly in Google Colab, Jupyter, or any Python script:

```python
import quantsynthica as qs

# 1. Direct Market Quote
quote = qs.get_quote("RELIANCE")
print(f"Price: {quote.price} | P/E: {quote.pe_ratio}")

# 2. Complete 4-in-1 Valuation Suite
val = qs.get_valuation("RELIANCE")
print(f"DCF Fair Value:     {val.dcf.fair_value_per_share}")
print(f"Piotroski Score:    {val.piotroski.f_score} / 9 ({val.piotroski.rating})")
print(f"Altman Z-Score:     {val.altman_z.z_score} ({val.altman_z.zone})")
print(f"Graham Number:      {val.graham.graham_number}")

# 3. Modern Portfolio Theory Optimization
opt = qs.optimize_portfolio(["RELIANCE", "TCS", "INFY"], objective="max_sharpe")
print("Expected Return:", opt.optimal_portfolio.expected_annual_return_pct, "%")
for a in opt.allocations:
    print(f"  {a.symbol}: {a.weight_pct}%")

# 4. Multi-Asset Screener (TradingView)
stocks = qs.screener.value_stocks(market="india", limit=10)
crypto = qs.screener.crypto(limit=10)
```

### The `Ticker` Object (OOP Interface)

```python
stock = qs.Ticker("TCS")

# Live quote
q = stock.quote()

# Historical OHLCV DataFrame
df = stock.history(period="1y")

# Technical indicators (SMA, RSI, MACD, Bollinger Bands)
tech = stock.technicals()
print("RSI 14:", tech.rsi_14)

# Custom Discounted Cash Flow (DCF)
dcf = stock.dcf(growth_rate=0.14, discount_rate=0.10)
print("Fair Value per share:", dcf.fair_value_per_share)

# Company news sentiment
news = stock.sentiment()
print("News Sentiment:", news.overall_sentiment)
```


---

## Key Features & Examples

### 1. Valuation Models (DCF, Piotroski, Altman Z, Graham)

```python
# Comprehensive valuation overview
val = client.valuation.get_overview("RELIANCE")
print("DCF Fair Value:", val.dcf_model.fair_value_per_share)
print("Piotroski Score:", val.piotroski_f_score.f_score, "/ 9")
print("Altman Zone:", val.altman_z_score.zone)
print("Graham Number:", val.graham_valuation.graham_number)

# Custom Discounted Cash Flow (DCF) calculation
custom_dcf = client.valuation.dcf(
    symbol="TCS",
    growth_rate=0.14,           # 14% annual growth
    discount_rate=0.105,        # 10.5% WACC hurdle
    terminal_growth_rate=0.035, # 3.5% perpetual growth
    years=5
)
print("Custom Fair Value:", custom_dcf.fair_value_per_share)
```

---

### 2. Portfolio Optimization (MPT / Markowitz Efficient Frontier)

```python
opt = client.portfolio.optimize(
    symbols=["RELIANCE", "TCS", "INFY", "HDFCBANK"],
    objective="max_sharpe",     # 'max_sharpe' or 'min_volatility'
    period="1y",
    include_frontier=True
)

print("Expected Annual Return:", opt.optimal_portfolio.expected_annual_return_pct, "%")
print("Annual Volatility:", opt.optimal_portfolio.annual_volatility_pct, "%")
print("Sharpe Ratio:", opt.optimal_portfolio.sharpe_ratio)

for alloc in opt.allocations:
    print(f"  {alloc.symbol}: {alloc.weight_pct}%")
```

---

### 3. Algorithmic Strategy Backtesting

```python
backtest = client.portfolio.backtest(
    symbol="RELIANCE",
    strategy="sma_crossover",
    period="2y",
    params={"fast_period": 20, "slow_period": 50},
    initial_capital=100000.0
)

print("Total Return:", backtest.summary.total_return_pct, "%")
print("Benchmark Return:", backtest.summary.benchmark_return_pct, "%")
print("Max Drawdown:", backtest.summary.max_drawdown_pct, "%")
print("Win Rate:", backtest.summary.win_rate_pct, "%")
print("Total Trades Executed:", len(backtest.trades))
```

---

### 4. Multi-Asset Screener (TradingView)

```python
# Screen value stocks
value_stocks = client.screener.value_stocks(market="india", limit=25)

# Screen crypto pairs
crypto_movers = client.screener.crypto(limit=20, sort_by="volume")

# Custom screen with SQL-like filters
custom_screen = client.screener.query(
    market="america",
    columns=["name", "close", "volume", "market_cap_basic", "price_earnings_ttm"],
    sort_by="market_cap_basic",
    limit=50
)
```

---

### 5. Financial Sentiment & NLP

```python
# Company news sentiment index
sentiment = client.sentiment.get_symbol_sentiment("RELIANCE")
print("Overall Sentiment:", sentiment.overall_sentiment)
print("Bullish Articles:", sentiment.breakdown.bullish_articles)

# Ad-hoc financial headline analysis
analysis = client.sentiment.analyze_text("Quarterly profit surges 35% beating analyst consensus estimates")
print(analysis.label, analysis.compound_score)
```

---

### 6. Institutional Factsheets & Excel Export

```python
# Download multi-tab Excel financial model
client.reports.download_excel("RELIANCE", output_path="reliance_model.xlsx")

# Retrieve printable HTML tearsheet
tearsheet_html = client.reports.get_tearsheet_html("RELIANCE")
```

---

## Error Handling

The SDK provides explicit exceptions:

```python
from quantsynthica import QuantSynthica
from quantsynthica.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    QuantSynthicaError
)

client = QuantSynthica(api_key="your_api_key")

try:
    quote = client.market.get_quote("UNKNOWN_TICKER")
except NotFoundError:
    print("Symbol does not exist")
except RateLimitError:
    print("Rate limit reached; retry shortly")
except AuthenticationError:
    print("Invalid API Key")
except QuantSynthicaError as e:
    print(f"API Error: {e.message} (HTTP {e.status_code})")
```

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
