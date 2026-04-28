from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models import Order, Payment


class OrderRepository(ABC):
    @abstractmethod
    def create(self, order) -> Order:
        pass

    @abstractmethod
    def get_by_id(self, order_id) -> Order:
        pass

    @abstractmethod
    def get_by_idempotency_key(self, idempotency_key: UUID | str) -> Order:
        pass

    @abstractmethod
    def update(self, order) -> Order:
        pass


class PaymentRepository(ABC):
    @abstractmethod
    def create(self, payment) -> Payment:
        pass

    @abstractmethod
    def get_by_order(self, order_id) -> Payment:
        pass

    @abstractmethod
    def update(self, payment) -> Payment:
        pass
