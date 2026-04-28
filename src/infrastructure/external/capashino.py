import logging
from urllib.parse import urljoin, urlunsplit, urlsplit
from uuid import UUID, uuid4

import requests
from abc import ABC

from src.application.ports.services import (
    NotificationService,
    CatalogService,
    PaymentService,
)
from src.domain.models import Item, Order

log = logging.getLogger(__name__)


class CapashinoBaseClient(ABC):
    def __init__(self, api_key: str, base_url: str, **kwargs):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") + "/"
        super().__init__(**kwargs)

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = urljoin(self.base_url, path.lstrip("/"))
        headers = kwargs.pop("headers", {})
        headers["X-API-Key"] = self.api_key
        log.debug(
            "Requesting URL: %s %s; headers: %s, body: %s", method, url, headers, kwargs
        )
        response = requests.request(method, url, headers=headers, **kwargs)
        if not response.ok:
            log.error("API error %s: %s", response.status_code, response.text)
            response.raise_for_status()
        result = response.json()
        log.debug("Capashino Response: %s", result)
        return result


class CatalogClient(CapashinoBaseClient, CatalogService):
    def get_item(self, item_id: UUID) -> Item:
        item = self._request(method="GET", path=f"api/catalog/items/{item_id}")
        log.debug("Item: %s", item)
        return Item(**item)


class PaymentClient(CapashinoBaseClient, PaymentService):
    def _gen_callback_url(self) -> str:
        callback_base_url = urlunsplit(
            urlsplit("//" + self.callback_base_url, scheme="http")
        )
        return urljoin(callback_base_url + "/", "api/orders/payment-callback")

    def create_payment(self, order: Order, amount: str) -> dict:
        log.debug("Creating payment for Order: %s, amount: %s", order, amount)
        payment = self._request(
            method="POST",
            path="api/payments",
            json={
                "order_id": str(order.id),
                "amount": amount,
                "callback_url": self._gen_callback_url(),
                "idempotency_key": str(uuid4()),
            },
        )
        del payment["created_at"]
        return payment


class NotificationClient(CapashinoBaseClient, NotificationService):
    def _build_message(self, status: str) -> str:
        msg_dict = {
            "NEW": "NEW: Ваш заказ создан и ожидает оплаты.",
            "PAID": "PAID: Ваш заказ успешно оплачен и готов к отправке.",
            "SHIPPED": "SHIPPED: Ваш заказ отправлен в доставку.",
            "CANCELLED": "CANCELLED: Ваш заказ отменен.",
        }
        return msg_dict[status]

    def send_notification(
        self, status: str, order_id: UUID, idempotency_key: UUID
    ) -> dict:
        response = self._request(
            method="POST",
            path="api/notifications",
            json={
                "message": self._build_message(status),
                "reference_id": str(order_id),
                "idempotency_key": str(idempotency_key),
            },
        )
        log.debug("Send Notification response: %s", response)
        return response
