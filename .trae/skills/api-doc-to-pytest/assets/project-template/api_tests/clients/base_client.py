from typing import Any, Dict, Optional

import requests


class BaseClient:
    def __init__(self, base_url: str, default_headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        merged_headers = {**self.default_headers, **(headers or {})}
        url = f"{self.base_url}{path}"
        return requests.request(method=method, url=url, params=params, json=json, headers=merged_headers, timeout=15, **kwargs)
