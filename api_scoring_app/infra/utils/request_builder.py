from __future__ import annotations

import requests

from typing import Any, Dict, Optional



class RequestBuilder:
    """
    Supports only GET requests, we don't need more.
    """

    def __init__(self):
        self._url: Optional[str] = None
        self._headers: Dict[str, str] = {}
        self._query_params: Dict[str, str] = {}
        self._body: Optional[Any] = None
        self._timeout: int = 5

    def with_url(self, url: str) -> RequestBuilder:
        self._url = url
        return self
    
    def with_headers(self, headers: Dict[str, str]) -> RequestBuilder:
        self._headers.update(headers)
        return self
    
    def with_query_params(self, params: Dict[str, str]) -> RequestBuilder:
        self._query_params.update(params)
        return self
    
    def with_timeout(self, timeout_seconds: int) -> RequestBuilder:
        self._timeout = timeout_seconds
        return self
    
    def _build(self) -> Dict[str, Any]:
        if not self._url:
            raise ValueError("URL is required")

        request = {
            "url": self._url,
            "timeout": self._timeout
        }

        if self._headers:
            request["headers"] = self._headers

        if self._query_params:
            request["params"] = self._query_params

        if self._body is not None:
            request["data"] = self._body

        return request
    
    def get(self) -> requests.Response:
        request_config = self._build()

        response = requests.get(
            url=request_config["url"],
            headers=request_config.get("headers", {}),
            params=request_config.get("params", {}),
            timeout=request_config["timeout"]
        )

        response.raise_for_status()

        return response
