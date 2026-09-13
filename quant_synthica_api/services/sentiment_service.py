"""Financial sentiment service combining provider news feeds with NLP sentiment engine."""

import time
from typing import Dict, Any, List
from quant_synthica_api.core.config import get_settings
from quant_synthica_api.services.symbol_resolver import SymbolResolver
from quant_synthica_api.services.market_service import MarketService
from quant_synthica_api.services.cache_service import cache
from quant_synthica_api.quant.sentiment import analyze_financial_sentiment

settings = get_settings()


class SentimentService:
    def __init__(self, market_service: MarketService):
        self.market = market_service

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze arbitrary text payload."""
        t0 = time.monotonic()
        res = analyze_financial_sentiment(text)
        res["latency_ms"] = round((time.monotonic() - t0) * 1000, 2)
        return res

    def get_symbol_news_sentiment(self, symbol_input: str) -> Dict[str, Any]:
        """Fetch news for symbol and compute aggregate sentiment and itemized article sentiment."""
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"sentiment:{resolved.canonical}:news"

        cached = cache.get_json(cache_key)
        if cached:
            cached["cached"] = True
            return cached

        news_res = self.market.get_news(resolved.canonical)
        articles = getattr(news_res, "news", getattr(news_res, "data", [])) or []

        analyzed_articles: List[Dict[str, Any]] = []
        compound_scores: List[float] = []

        for art in articles:
            # Combine title and publisher info
            text_to_score = f"{art.title}. "
            sentiment = analyze_financial_sentiment(text_to_score)
            compound_scores.append(sentiment["compound_score"])

            analyzed_articles.append({
                "title": art.title,
                "publisher": art.publisher,
                "link": art.link,
                "published_at": getattr(art, "published_at", None),
                "sentiment_label": sentiment["label"],
                "compound_score": sentiment["compound_score"],
                "pos": sentiment["pos"],
                "neg": sentiment["neg"],
                "neu": sentiment["neu"],
                "keywords": sentiment["detected_keywords"],
            })


        if compound_scores:
            avg_compound = round(sum(compound_scores) / len(compound_scores), 4)
            pos_count = sum(1 for a in analyzed_articles if a["sentiment_label"] == "Bullish")
            neg_count = sum(1 for a in analyzed_articles if a["sentiment_label"] == "Bearish")
            neu_count = sum(1 for a in analyzed_articles if a["sentiment_label"] == "Neutral")
            total = len(compound_scores)
        else:
            avg_compound = 0.0
            pos_count = neg_count = neu_count = 0
            total = 0

        if avg_compound >= 0.25:
            overall = "Strongly Bullish"
        elif avg_compound >= 0.08:
            overall = "Bullish"
        elif avg_compound <= -0.25:
            overall = "Strongly Bearish"
        elif avg_compound <= -0.08:
            overall = "Bearish"
        else:
            overall = "Neutral"

        response_data = {
            "symbol": resolved.canonical,
            "overall_sentiment": overall,
            "mean_compound_score": avg_compound,
            "total_articles_analyzed": total,
            "breakdown": {
                "bullish_articles": pos_count,
                "bearish_articles": neg_count,
                "neutral_articles": neu_count,
                "bullish_pct": round((pos_count / total * 100), 1) if total > 0 else 0.0,
                "bearish_pct": round((neg_count / total * 100), 1) if total > 0 else 0.0,
                "neutral_pct": round((neu_count / total * 100), 1) if total > 0 else 0.0,
            },
            "articles": analyzed_articles,
            "cached": False,
            "latency_ms": round((time.monotonic() - t0) * 1000, 2),
        }

        cache.set_json(cache_key, response_data, ttl=settings.CACHE_QUANT_TTL)
        return response_data

