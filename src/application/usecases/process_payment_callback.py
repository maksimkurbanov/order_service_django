import logging
from uuid import uuid4

from src.application.dto import PaymentUpdateDTO, OrderUpdateDTO, OutboxEventCreateDTO
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.models import Payment
from src.domain.value_objects import (
    OrderStatusEnum,
    OutboxEventTypeEnum,
    OutboxEventStatusEnum,
)

log = logging.getLogger(__name__)


class ProcessPaymentCallbackUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    def __call__(self, payment: dict) -> Payment:
        log.debug("Processing payment callback request with data: %s", payment)
        with self._unit_of_work as uow:
            try:
                existing_payment = uow.payment_repo.get_by_order(payment["order_id"])
                if (
                    existing_payment
                    and existing_payment.status != payment["status"].upper()
                ):
                    existing_payment = uow.payment_repo.update(
                        PaymentUpdateDTO(
                            id=payment["payment_id"], status=payment["status"].upper()
                        ),
                    )
                    inc_order_status = OrderStatusEnum.from_payment_status(
                        payment["status"]
                    )
                    order = uow.order_repo.update(
                        OrderUpdateDTO(id=payment["order_id"], status=inc_order_status)
                    )
                    outbox_id = str(uuid4())
                    event_type = OutboxEventTypeEnum.from_payment_status(
                        payment["status"]
                    )
                    uow.outbox_repo.create(
                        OutboxEventCreateDTO(
                            id=outbox_id,
                            order_id=existing_payment.order_id,
                            event_type=event_type,
                            payload={
                                "event_type": event_type.lower(),
                                "order_id": str(order.id),
                                "item_id": str(order.item_id),
                                "quantity": order.quantity,
                                "idempotency_key": outbox_id,
                            },
                            status=OutboxEventStatusEnum.PENDING,
                        )
                    )
                    uow.commit()
                return existing_payment
            except Exception as e:
                log.error("Failed to process payment callback: %s", str(e))
