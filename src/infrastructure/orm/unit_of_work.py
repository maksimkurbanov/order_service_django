from django.db import transaction

from src.domain.interfaces import UnitOfWork
from src.infrastructure.orm.repositories import (
    DjangoOrderRepository,
    DjangoPaymentRepository,
    DjangoOutboxRepository,
    DjangoInboxRepository,
)


class DjangoUnitOfWork(UnitOfWork):
    def __init__(self):
        self._atomic = transaction.atomic()
        self.order_repo = DjangoOrderRepository()
        self.payment_repo = DjangoPaymentRepository()
        self.outbox_repo = DjangoOutboxRepository()
        self.inbox_repo = DjangoInboxRepository()

    def __enter__(self):
        self._atomic.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._atomic.__exit__(exc_type, exc_val, exc_tb)

    def commit(self):
        pass

    def rollback(self):
        pass
