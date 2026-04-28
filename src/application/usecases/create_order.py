import logging
from decimal import Decimal
from uuid import uuid4

from src.application.dto import (
    OrderCreateDTO,
    OrderUpdateDTO,
    PaymentCreateDTO,
    OutboxEventCreateDTO,
)
from src.application.exceptions import InsufficientStockError
from src.application.ports.services import CatalogService, PaymentService
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.models import Order
from src.domain.value_objects import (
    OrderStatusEnum,
    OutboxEventTypeEnum,
    OutboxEventStatusEnum,
)


log = logging.getLogger(__name__)


class CreateOrderUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        catalog_client: CatalogService,
        payment_client: PaymentService,
    ):
        self._uow = unit_of_work
        self._catalog_client = catalog_client
        self._payment_client = payment_client

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
                outbox_id = str(uuid4())
                uow.outbox_repo.create(
                    OutboxEventCreateDTO(
                        id=outbox_id,
                        order_id=new_order.id,
                        event_type=OutboxEventTypeEnum.CREATED,
                        payload={
                            "event_type": OutboxEventTypeEnum.CREATED.lower(),
                            "order_id": str(new_order.id),
                            "item_id": str(new_order.item_id),
                            "quantity": new_order.quantity,
                            "idempotency_key": outbox_id,
                        },
                        status=OutboxEventStatusEnum.PENDING,
                    )
                )
                amount = f"{(Decimal(new_order.quantity) * Decimal(item.price)):.2f}"
                payment = self._payment_client.create_payment(new_order, amount)
                uow.payment_repo.create(PaymentCreateDTO(**payment))
                uow.commit()
            except Exception as e:
                new_order = uow.order_repo.update(
                    OrderUpdateDTO(id=new_order.id, status=OrderStatusEnum.CANCELLED)
                )
                outbox_id = str(uuid4())
                uow.outbox_repo.create(
                    OutboxEventCreateDTO(
                        id=outbox_id,
                        order_id=new_order.id,
                        event_type=OutboxEventTypeEnum.CANCELLED,
                        payload={
                            "event_type": OutboxEventTypeEnum.CREATED.lower(),
                            "order_id": str(new_order.id),
                            "item_id": str(new_order.item_id),
                            "quantity": new_order.quantity,
                            "idempotency_key": outbox_id,
                        },
                        status=OutboxEventStatusEnum.PENDING,
                    )
                )
                log.error("Failed to create order: %s", str(e))
                uow.commit()
            return new_order
