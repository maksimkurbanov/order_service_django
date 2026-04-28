from django.db import transaction

from src.application.ports.unit_of_work import UnitOfWork
from src.infrastructure.orm.repositories import (
    DjangoOrderRepository,
    DjangoPaymentRepository,
    DjangoOutboxRepository,
    DjangoInboxRepository,
)


class DjangoUnitOfWork(UnitOfWork):
    def __init__(
        self,
        order_repo: DjangoOrderRepository,
        payment_repo: DjangoPaymentRepository,
        outbox_repo: DjangoOutboxRepository,
        inbox_repo: DjangoInboxRepository,
    ):
        self._atomic = transaction.atomic()
        self.order_repo = order_repo
        self.payment_repo = payment_repo
        self.outbox_repo = outbox_repo
        self.inbox_repo = inbox_repo

    def __enter__(self):
        self._atomic.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._atomic.__exit__(exc_type, exc_val, exc_tb)

    def commit(self):
        pass

    def rollback(self):
        pass
