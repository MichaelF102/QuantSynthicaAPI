from typing import Optional, Any, Dict
from fastapi import HTTPException, status

class QuantSynthicaException(Exception):
    """Base exception for QuantSynthica API"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class SymbolResolutionError(QuantSynthicaException):
    """Raised when a symbol cannot be resolved"""
    pass

class ProviderError(QuantSynthicaException):
    """Raised when a provider encounters a failure"""
    def __init__(self, provider: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Provider '{provider}' failed: {message}", details)
        self.provider = provider

class ProviderRateLimitError(ProviderError):
    """Raised when a provider rate limits requests"""
    pass

class NormalizationError(QuantSynthicaException):
    """Raised when data cannot be normalized"""
    pass

class QuantCalculationError(QuantSynthicaException):
    """Raised when a quantitative metric calculation fails"""
    pass
