"""Financial sentiment engine."""

import re
from quantsynthica.resources.base import DotDict

FINANCIAL_LEXICON = {
    "surge": 2.5, "surges": 2.5, "surged": 2.5, "rally": 2.4, "rallies": 2.4,
    "beat": 2.2, "beats": 2.2, "upgrade": 2.5, "upgraded": 2.5, "bullish": 2.4,
    "profit": 1.8, "growth": 1.7, "dividend": 1.5, "rebound": 1.9,
    "plunge": -2.8, "plunges": -2.8, "slump": -2.5, "slumps": -2.5,
    "miss": -2.2, "misses": -2.2, "downgrade": -2.6, "bearish": -2.4,
    "loss": -2.0, "losses": -2.0, "debt": -1.2, "default": -3.2,
    "bankruptcy": -3.5, "fraud": -3.8,
}


def analyze_sentiment(text: str) -> DotDict:
    if not text:
        return DotDict({"compound_score": 0.0, "label": "Neutral", "detected_keywords": []})

    words = re.findall(r"\b[a-z0-9\-]+\b", text.lower())
    detected = [w for w in words if w in FINANCIAL_LEXICON]
    total_score = sum(FINANCIAL_LEXICON.get(w, 0.0) for w in words)
    denom = max(1.0, len(words) ** 0.5)
    compound = max(-1.0, min(1.0, round(total_score / (denom * 2.0), 4)))

    if compound >= 0.15:
        label = "Bullish"
    elif compound <= -0.15:
        label = "Bearish"
    else:
        label = "Neutral"

    return DotDict({
        "compound_score": compound,
        "label": label,
        "detected_keywords": list(set(detected)),
    })
