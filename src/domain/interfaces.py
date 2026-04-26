from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dto import (
    OrderCreateDTO,
    PaymentUpdateDTO,
    PaymentCreateDTO,
    OrderUpdateDTO,
)
from src.domain.models import Order, InboxEvent, OutboxEvent, Item
from src.infrastructure.orm.models import Payment


class OrderRepository(ABC):
    @abstractmethod
    def create(self, order: OrderCreateDTO) -> Order:
        pass

    @abstractmethod
    def get_by_id(self, order_id: UUID) -> Order:
        pass

    @abstractmethod
    def get_by_idempotency_key(self, idempotency_key: UUID | str) -> Order:
        pass

    @abstractmethod
    def update(self, order: OrderUpdateDTO) -> Order:
        pass


class PaymentRepository(ABC):
    @abstractmethod
    def create(self, payment: PaymentCreateDTO) -> Payment:
        pass

    @abstractmethod
    def get_by_order(self, order_id: UUID) -> Payment:
        pass

    @abstractmethod
    def update(self, payment: PaymentUpdateDTO) -> Payment:
        pass


class OutboxRepository(ABC):
    @abstractmethod
    def create(self, event: OutboxEvent):
        pass

    @abstractmethod
    def get_pending(self):
        pass

    @abstractmethod
    def mark_published(self, event_id):
        pass


class InboxRepository(ABC):
    def create(self, event: InboxEvent):
        pass

    @abstractmethod
    def get_pending(self):
        pass

    @abstractmethod
    def mark_processed(self, event_id):
        pass


class UnitOfWork(ABC):
    order_repo: OrderRepository
    payment_repo: PaymentRepository
    outbox_repo: OutboxRepository
    inbox_repo: InboxRepository

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class CatalogService(ABC):
    @abstractmethod
    def get_item(self, item_id: UUID) -> Item:
        pass


class PaymentService(ABC):
    @abstractmethod
    def _gen_callback_url(self) -> str:
        pass

    @abstractmethod
    def create_payment(self, order, amount: str) -> dict:
        pass


class NotificationService(ABC):
    @abstractmethod
    def _build_msg(self, status: str) -> dict:
        pass

    @abstractmethod
    def send_notification(
        self, status: str, order_id: UUID, idempotency_key: UUID
    ) -> None:
        pass
