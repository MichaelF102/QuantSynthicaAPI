"""Exceptions raised by the QuantSynthica Python SDK."""

from typing import Optional, Any


class QuantSynthicaError(Exception):
    """Base exception class for all QuantSynthica SDK errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(QuantSynthicaError):
    """Raised when API key is missing, invalid, or unauthorized (401/403)."""
    pass


class NotFoundError(QuantSynthicaError):
    """Raised when the requested symbol or endpoint is not found (404)."""
    pass


class ValidationError(QuantSynthicaError):
    """Raised when request payload or parameters fail validation (422)."""
    pass


class RateLimitError(QuantSynthicaError):
    """Raised when request rate limits or upstream throttling are exceeded (429)."""
    pass


class ServerInternalError(QuantSynthicaError):
    """Raised when the QuantSynthica server or upstream provider encounters an error (500/502)."""
    pass


class APIConnectionError(QuantSynthicaError):
    """Raised when the client cannot connect to the QuantSynthica API server."""
    pass
