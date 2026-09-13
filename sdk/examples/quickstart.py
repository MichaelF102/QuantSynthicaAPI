"""Quickstart example for the QuantSynthica Python SDK."""

import os
from quantsynthica import QuantSynthica

def main():
    # Initialize client (uses localhost:8000 by default)
    api_key = os.getenv("QUANTSYNTHICA_API_KEY", "qs_live_dev_secret_key_12345")
    base_url = os.getenv("QUANTSYNTHICA_BASE_URL", "http://localhost:8000")

    print(f"Connecting to QuantSynthica API at {base_url}...")
    client = QuantSynthica(api_key=api_key, base_url=base_url)

    # 1. Health check
    health = client.stocks.health()
    print(f"Status: {health.status} | Version: {health.version}")

    # 2. Market Quote
    symbol = "RELIANCE"
    quote = client.market.get_quote(symbol)
    print(f"\n--- {symbol} Quote ---")
    print(f"Price: {quote.data.price}")
    print(f"Day Change: {quote.data.change} ({quote.data.change_percent}%)")
    print(f"Market Cap: {quote.data.market_cap:,.0f}" if quote.data.market_cap else "Market Cap: N/A")

    # 3. Valuation Overview
    val = client.valuation.get_overview(symbol)
    print(f"\n--- {symbol} Valuation Models ---")
    print(f"DCF Fair Value: {val.dcf_model.fair_value_per_share}")
    print(f"Piotroski Score: {val.piotroski_f_score.f_score}/9 ({val.piotroski_f_score.rating})")
    print(f"Altman Z-Score: {val.altman_z_score.z_score} ({val.altman_z_score.zone})")
    print(f"Graham Number: {val.graham_valuation.graham_number}")

    # 4. Financial Sentiment
    sentiment = client.sentiment.get_symbol_sentiment(symbol)
    print(f"\n--- {symbol} News Sentiment ---")
    print(f"Overall Sentiment: {sentiment.overall_sentiment} (Compound: {sentiment.mean_compound_score})")
    print(f"Articles Analyzed: {sentiment.total_articles_analyzed}")

    # 5. Portfolio Optimization
    symbols = ["RELIANCE", "TCS", "INFY"]
    print(f"\n--- Portfolio Optimization for {symbols} ---")
    opt = client.portfolio.optimize(symbols=symbols, objective="max_sharpe")
    print(f"Expected Annual Return: {opt.optimal_portfolio.expected_annual_return_pct}%")
    print(f"Annual Volatility: {opt.optimal_portfolio.annual_volatility_pct}%")
    print(f"Sharpe Ratio: {opt.optimal_portfolio.sharpe_ratio}")
    print("Allocations:")
    for alloc in opt.allocations:
        print(f"  {alloc.symbol}: {alloc.weight_pct}%")

if __name__ == "__main__":
    main()
