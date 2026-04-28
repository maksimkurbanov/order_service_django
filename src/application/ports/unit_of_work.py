from abc import ABC, abstractmethod

from src.application.ports.repositories import OutboxRepository, InboxRepository
from src.domain.interfaces import OrderRepository, PaymentRepository


class UnitOfWork(ABC):
    order_repo: OrderRepository
    payment_repo: PaymentRepository
    outbox_repo: OutboxRepository
    inbox_repo: InboxRepository

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
