from uuid import UUID

from src.application.ports.unit_of_work import UnitOfWork
from src.domain.models import Order


class GetOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self.uow = unit_of_work

    def __call__(self, order_id: UUID) -> Order:
        with self.uow as uow:
            try:
                order = uow.order_repo.get_by_id(order_id)
            except ValueError as e:
                raise e
            return order
