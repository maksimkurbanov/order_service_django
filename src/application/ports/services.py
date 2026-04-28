from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models import Item


class CatalogService(ABC):
    @abstractmethod
    def get_item(self, item_id: UUID) -> Item:
        pass


class PaymentService(ABC):
    def __init__(self, callback_base_url: str, **kwargs):
        self.callback_base_url = callback_base_url.rstrip("/")
        super().__init__(**kwargs)

    @abstractmethod
    def _gen_callback_url(self) -> str:
        pass

    @abstractmethod
    def create_payment(self, order, amount: str) -> dict:
        pass


class NotificationService(ABC):
    @abstractmethod
    def _build_message(self, status: str) -> dict:
        pass

    @abstractmethod
    def send_notification(
        self, status: str, order_id: UUID, idempotency_key: UUID
    ) -> None:
        pass
