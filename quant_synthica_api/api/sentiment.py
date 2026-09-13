"""Financial Sentiment & NLP API endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from quant_synthica_api.core.security import verify_api_key
from quant_synthica_api.services.container import container
from quant_synthica_api.services.sentiment_service import SentimentService

router = APIRouter(prefix="/sentiment", tags=["Financial Sentiment & NLP"], dependencies=[Depends(verify_api_key)])


def get_sentiment_service() -> SentimentService:
    return container.sentiment_service


class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., description="Financial text, article snippet, earnings commentary, or headline to analyze")


@router.get("/{symbol}")
def get_symbol_sentiment(
    symbol: str,
    service: SentimentService = Depends(get_sentiment_service),
) -> Dict[str, Any]:
    """Retrieve aggregate sentiment and article-level sentiment breakdown for recent company news."""
    return service.get_symbol_news_sentiment(symbol)


@router.post("/analyze")
def analyze_text_sentiment(
    req: AnalyzeTextRequest,
    service: SentimentService = Depends(get_sentiment_service),
) -> Dict[str, Any]:
    """Analyze sentiment polarity, compound score, and financial keywords for arbitrary text."""
    return service.analyze_text(req.text)
