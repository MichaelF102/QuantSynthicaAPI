"""Financial sentiment & NLP resource."""

from quantsynthica.resources.base import BaseResource, DotDict


class SentimentResource(BaseResource):
    def get_symbol_sentiment(self, symbol: str) -> DotDict:
        """Get company news sentiment score, polarity breakdown, and article items."""
        return self._request("GET", f"sentiment/{symbol}")

    def analyze_text(self, text: str) -> DotDict:
        """Analyze arbitrary financial headline or commentary text."""
        return self._request("POST", "sentiment/analyze", json_data={"text": text})
