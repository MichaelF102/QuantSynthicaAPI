from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Any, Dict
from datetime import datetime, timezone
import time

T = TypeVar("T")

class ProviderResult(Generic[T]):
    def __init__(
        self,
        data: Optional[T],
        provider: str,
        success: bool = True,
        error: Optional[str] = None,
        latency_ms: Optional[float] = None,
        cached: bool = False
    ):
        self.data = data
        self.provider = provider
        self.success = success
        self.error = error
        self.latency_ms = latency_ms
        self.cached = cached
        self.retrieved_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "success": self.success,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "cached": self.cached,
            "retrieved_at": self.retrieved_at.isoformat()
        }

class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def health_check(self) -> bool:
        pass
