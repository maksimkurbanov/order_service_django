import logging
from urllib.parse import urljoin
from uuid import UUID

import requests
from abc import ABC

from src.domain.interfaces import CatalogService
from src.domain.models import Item


log = logging.getLogger(__name__)


class CapashinoBaseClient(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") + "/"

    def _request(self, method: str, path: str, **kwargs):
        url = urljoin(self.base_url, path.lstrip("/"))
        headers = kwargs.pop("headers", {})
        headers["X-API-Key"] = self.api_key
        log.debug(
            "Requesting URL: %s %s; headers: %s, body: %s", method, url, headers, kwargs
        )
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        result = response.json()
        log.debug("Capashino Response: %s", result)
        return result


class CatalogClient(CapashinoBaseClient, CatalogService):
    def get_item(self, item_id: UUID) -> Item:
        item = self._request(method="GET", path=f"api/catalog/items/{item_id}")
        return Item(**item)
