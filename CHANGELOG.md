# Changelog

All notable changes to the **QuantSynthica** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.1] - 2026-09-13

### Added
- **Direct Financial Statements**: Added top-level convenience functions and `Ticker` methods:
  - `qs.get_financials(symbol, quarterly=False)` for Income Statement DataFrames.
  - `qs.get_balance_sheet(symbol, quarterly=False)` for Balance Sheet statements.
  - `qs.get_cashflow(symbol, quarterly=False)` for Statements of Cash Flows.
- **Fundamental & Valuation Ratios**: `qs.get_ratios(symbol)` returning trailing & forward P/E, Price/Book, EV/EBITDA, EV/Revenue, Operating Margin, Net Margin, Return on Equity, and Debt/Equity.
- **Analyst Consensus & Targets**: `qs.get_analyst_targets(symbol)` returning mean, high, low, and median price targets, institutional recommendations, and analyst count.
- **Corporate Profile**: `qs.get_profile(symbol)` returning sector, industry classification, employee headcount, website, and business description.
- **Dividend History**: `Ticker.dividends()` returning historical cash payout series.
- **Official Google Colab Demo**: Created interactive Colab notebook (`notebooks/quantsynthica_colab_demo.ipynb`) covering all 15 core financial and quantitative workflows.

---

## [1.1.0] - 2026-09-13

### Added
- **Serverless Standalone Engine**: Transformed `quantsynthica` into a 100% zero-server, zero-cost Python library (like `yfinance`) that executes locally in Python, Jupyter, and Google Colab without needing any backend server or API key.
- **Embedded Valuation Suite**:
  - Discounted Cash Flow (DCF) model with configurable growth, WACC discount hurdle, and perpetual terminal growth.
  - Piotroski 9-point fundamental accounting F-Score.
  - Altman Z-Score credit risk & bankruptcy classification (Safe, Grey, Distress).
  - Benjamin Graham Number & Net-Net Working Capital per share.
- **Markowitz Modern Portfolio Theory (MPT)**: Quadratic SLSQP optimization solver for Maximum Sharpe Ratio and Minimum Volatility asset allocations.
- **Algorithmic Strategy Backtester**: Event-driven simulation engine for SMA Crossover, EMA Crossover, and RSI Mean Reversion with configurable commission, slippage, and equity curves.
- **Vectorized Technical Indicators**: Local calculations for SMA (20/50/200), EMA (12/26), RSI (14), MACD, and Bollinger Bands.
- **Direct Multi-Asset Screener**: Embedded `tradingview-screener` wrapper for Indian and global equities, crypto, and forex pairs.
- **Financial NLP Sentiment Engine**: Domain-specific financial dictionary scoring news feeds and commentary.
- **Object-Oriented Interface**: Added `qs.Ticker` and `qs.Stock` class interface.

---

## [1.0.0] - 2026-09-13

### Added
- **Initial PyPI Release**: Official client SDK for connecting to the QuantSynthica FastAPI microservice.
- **Resource Namespaces**: Strongly-typed modules: `market`, `fundamentals`, `screener`, `valuation`, `portfolio`, `sentiment`, `reports`, `stocks`, `quant`.
- **Error Hierarchy**: Custom exception classes (`QuantSynthicaError`, `AuthenticationError`, `NotFoundError`, `ValidationError`, `RateLimitError`, `ServerInternalError`, `APIConnectionError`).
- **Response Normalization**: Dot-accessible `DotDict` response structures.
