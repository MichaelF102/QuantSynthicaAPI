"""QuantSynthica Python Client SDK.

A unified Python client for live market quotes, historical OHLCV data, multi-asset screening,
financial statements, DCF valuation, Piotroski scoring, Modern Portfolio Theory optimization,
algorithmic backtesting, and sentiment analysis.
"""

from quantsynthica.client import QuantSynthica, Client
from quantsynthica.exceptions import (
    QuantSynthicaError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerInternalError,
    APIConnectionError,
)

__version__ = "1.0.0"
__all__ = [
    "QuantSynthica",
    "Client",
    "QuantSynthicaError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerInternalError",
    "APIConnectionError",
]
