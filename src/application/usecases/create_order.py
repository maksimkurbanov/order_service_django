import logging

from src.application.dto import OrderCreateDTO, OrderUpdateDTO
from src.application.exceptions import InsufficientStockError
from src.domain.interfaces import UnitOfWork
from src.domain.models import Order
from src.domain.value_objects import OrderStatusEnum
from src.infrastructure.external.capashino import CatalogClient

log = logging.getLogger(__name__)


class CreateOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWork, catalog_client: CatalogClient):
        self._uow = unit_of_work
        self._catalog_client = catalog_client

    def __call__(self, order: dict) -> Order:
        with self._uow as uow:
            if order.get("idempotency_key"):
                try:
                    existing_order = uow.order_repo.get_by_idempotency_key(
                        order["idempotency_key"]
                    )
                    if existing_order:
                        log.debug(
                            "Idempotency key %s in DB, creation aborted, returning DB entry",
                            order["idempotency_key"],
                        )
                        return existing_order
                except ValueError:
                    log.debug(
                        "Idempotency key %s not in DB, proceeding with order creation",
                        order["idempotency_key"],
                    )
            item = self._catalog_client.get_item(order["item_id"])
            if item.available_qty < order["quantity"]:
                raise InsufficientStockError("Insufficient stock")

            try:
                new_order = uow.order_repo.create(
                    OrderCreateDTO(**order, status=OrderStatusEnum.NEW)
                )
                uow.commit()
            except Exception as e:
                uow.order_repo.update(
                    OrderUpdateDTO(id=new_order.id, status=OrderStatusEnum.CANCELLED)
                )
                log.error("Failed to create order: %s", str(e))
                uow.commit()
                raise
            return new_order
