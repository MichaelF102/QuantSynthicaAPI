"""Financial Sentiment and NLP Engine.

Augments lexicon-based sentiment analysis with domain-specific finance vocabulary
(earnings surprises, ratings changes, dividends, insolvency, executive turnover).
"""

from typing import Dict, Any, List, Optional
import re

# Domain-specific financial dictionary
FINANCIAL_LEXICON = {
    # Bullish terms
    "surge": 2.6,
    "surges": 2.6,
    "surged": 2.6,
    "rally": 2.4,
    "rallies": 2.4,
    "rallied": 2.4,
    "outperform": 2.5,
    "outperformed": 2.5,
    "beat": 2.2,
    "beats": 2.2,
    "upgrade": 2.5,
    "upgraded": 2.5,
    "bullish": 2.4,
    "buy": 1.8,
    "strong buy": 3.0,
    "record high": 2.8,
    "all-time high": 2.8,
    "profit": 1.8,
    "profitable": 1.8,
    "growth": 1.7,
    "dividend": 1.5,
    "bonus": 1.5,
    "expansion": 1.6,
    "turnaround": 2.0,
    "rebound": 1.9,
    "breakout": 1.8,
    "tailwind": 1.6,
    "upside": 1.8,
    # Bearish terms
    "plunge": -2.8,
    "plunges": -2.8,
    "plunged": -2.8,
    "slump": -2.5,
    "slumps": -2.5,
    "slumped": -2.5,
    "tumble": -2.6,
    "tumbles": -2.6,
    "underperform": -2.4,
    "underperformed": -2.4,
    "miss": -2.2,
    "misses": -2.2,
    "missed": -2.2,
    "downgrade": -2.6,
    "downgraded": -2.6,
    "bearish": -2.4,
    "sell": -1.8,
    "strong sell": -3.0,
    "loss": -2.0,
    "losses": -2.0,
    "decline": -1.8,
    "declined": -1.8,
    "fall": -1.6,
    "fell": -1.6,
    "drop": -1.6,
    "dropped": -1.6,
    "debt": -1.2,
    "default": -3.2,
    "defaulted": -3.2,
    "bankruptcy": -3.5,
    "insolvency": -3.2,
    "headwind": -1.7,
    "fraud": -3.8,
    "scam": -3.5,
    "investigation": -2.2,
    "penalty": -2.0,
    "lawsuit": -1.9,
    "subpoena": -2.5,
}

_vader_analyzer = None

def _get_analyzer():
    global _vader_analyzer
    if _vader_analyzer is None:
        try:
            import nltk
            try:
                from nltk.sentiment.vader import SentimentIntensityAnalyzer
                _vader_analyzer = SentimentIntensityAnalyzer()
                # Update with financial lexicon
                _vader_analyzer.lexicon.update(FINANCIAL_LEXICON)
            except Exception:
                nltk.download("vader_lexicon", quiet=True)
                from nltk.sentiment.vader import SentimentIntensityAnalyzer
                _vader_analyzer = SentimentIntensityAnalyzer()
                _vader_analyzer.lexicon.update(FINANCIAL_LEXICON)
        except Exception:
            _vader_analyzer = False
    return _vader_analyzer


def analyze_financial_sentiment(text: str) -> Dict[str, Any]:
    """Analyze the financial sentiment of a text string (headline, snippet, or report).

    Returns:
        compound: Normalized score between -1.0 (extreme bearish) and +1.0 (extreme bullish).
        label: 'Bullish', 'Bearish', or 'Neutral'.
        proportions: {pos, neg, neu}
        detected_keywords: List of financial terms detected.
    """
    if not text or not text.strip():
        return {
            "compound_score": 0.0,
            "label": "Neutral",
            "pos": 0.0,
            "neg": 0.0,
            "neu": 1.0,
            "detected_keywords": [],
        }

    lower_text = text.lower()
    words = re.findall(r"\b[a-z0-9\-]+\b", lower_text)
    detected_terms = [w for w in words if w in FINANCIAL_LEXICON]

    analyzer = _get_analyzer()
    if analyzer:
        scores = analyzer.polarity_scores(text)
        compound = round(float(scores["compound"]), 4)
        pos = round(float(scores["pos"]), 3)
        neg = round(float(scores["neg"]), 3)
        neu = round(float(scores["neu"]), 3)
    else:
        # Fallback pure-python financial sentiment computation
        total_score = sum(FINANCIAL_LEXICON.get(w, 0.0) for w in words)
        denom = max(1.0, len(words) ** 0.5)
        compound = max(-1.0, min(1.0, round(total_score / (denom * 2.0), 4)))
        pos_words = [w for w in detected_terms if FINANCIAL_LEXICON[w] > 0]
        neg_words = [w for w in detected_terms if FINANCIAL_LEXICON[w] < 0]
        total_detected = max(1, len(detected_terms))
        pos = round(len(pos_words) / total_detected, 3)
        neg = round(len(neg_words) / total_detected, 3)
        neu = round(max(0.0, 1.0 - (pos + neg)), 3)

    if compound >= 0.15:
        label = "Bullish"
    elif compound <= -0.15:
        label = "Bearish"
    else:
        label = "Neutral"

    return {
        "compound_score": compound,
        "label": label,
        "pos": pos,
        "neg": neg,
        "neu": neu,
        "detected_keywords": list(set(detected_terms)),
    }
