"""
Base API client.

Every other file in `api/` should build on top of `APIClient` instead of
calling `requests` directly, so timeouts, base URL and error handling stay
in one place. The backend base URL is read from the `API_BASE_URL`
environment variable so the frontend can point at localhost while
developing and at the real host in production without code changes.

See integration/README.md for how this wires up to the FastAPI backend.
"""

import os
import requests

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 30  # seconds


class APIError(Exception):
    """Raised whenever the backend returns an error or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class APIClient:
    def __init__(self, base_url: str | None = None, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = (base_url or os.getenv("API_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _handle(self, response: requests.Response):
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            raise APIError(detail, status_code=response.status_code)
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return response.content

    def get(self, path: str, params: dict | None = None):
        try:
            r = requests.get(self._url(path), params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise APIError(f"Could not reach backend: {exc}") from exc
        return self._handle(r)

    def post(self, path: str, json: dict | None = None, files: dict | None = None, data: dict | None = None):
        try:
            r = requests.post(self._url(path), json=json, files=files, data=data, timeout=self.timeout)
        except requests.RequestException as exc:
            raise APIError(f"Could not reach backend: {exc}") from exc
        return self._handle(r)

    def delete(self, path: str, params: dict | None = None):
        try:
            r = requests.delete(self._url(path), params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise APIError(f"Could not reach backend: {exc}") from exc
        return self._handle(r)


# Shared singleton — import `api_client` instead of constructing APIClient() everywhere.
api_client = APIClient()