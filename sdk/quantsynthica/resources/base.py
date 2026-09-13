"""Base Resource class handling HTTP transport and response parsing."""

from typing import Dict, Any, Optional
import httpx

from quantsynthica.exceptions import (
    QuantSynthicaError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerInternalError,
    APIConnectionError,
)


class DotDict(dict):
    """A dictionary subclass that allows attribute-style access (e.g. obj.price instead of obj['price'])."""
    def __getattr__(self, name: str) -> Any:
        try:
            val = self[name]
            if isinstance(val, dict) and not isinstance(val, DotDict):
                val = DotDict(val)
                self[name] = val
            return val
        except KeyError:
            raise AttributeError(f"'DotDict' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'DotDict' object has no attribute '{name}'")


def _wrap_response(data: Any) -> Any:
    if isinstance(data, dict):
        return DotDict({k: _wrap_response(v) for k, v in data.items()})
    elif isinstance(data, list):
        return [_wrap_response(i) for i in data]
    return data


class BaseResource:
    def __init__(self, client: "QuantSynthica"):
        self._client = client

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Any:
        url = f"{self._client.base_url.rstrip('/')}/api/v1/{path.lstrip('/')}"
        headers = {
            "User-Agent": f"quantsynthica-python/{self._client.version}",
            "Accept": "application/json",
        }
        if self._client.api_key:
            headers["X-API-Key"] = self._client.api_key

        # Filter None params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            resp = self._client._http_client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=self._client.timeout,
            )
        except httpx.RequestError as exc:
            raise APIConnectionError(f"Failed to connect to QuantSynthica API at {url}: {exc}") from exc

        if raw_response:
            if resp.status_code >= 400:
                self._handle_error(resp)
            return resp.content

        if resp.status_code >= 400:
            self._handle_error(resp)

        try:
            data = resp.json()
            return _wrap_response(data)
        except Exception:
            return resp.text

    def _handle_error(self, resp: httpx.Response) -> None:
        status = resp.status_code
        try:
            body = resp.json()
            message = body.get("message") or body.get("detail") or resp.text
        except Exception:
            body = None
            message = resp.text

        if status in (401, 403):
            raise AuthenticationError(f"Authentication failed: {message}", status, body)
        elif status == 404:
            raise NotFoundError(f"Resource not found: {message}", status, body)
        elif status == 422:
            raise ValidationError(f"Validation error: {message}", status, body)
        elif status == 429:
            raise RateLimitError(f"Rate limit exceeded: {message}", status, body)
        elif status >= 500:
            raise ServerInternalError(f"Server error: {message}", status, body)
        else:
            raise QuantSynthicaError(f"HTTP error {status}: {message}", status, body)
