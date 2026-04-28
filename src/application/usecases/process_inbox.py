import logging
from uuid import uuid4

from src.application.dto import (
    OrderUpdateDTO,
    OutboxEventCreateDTO,
    InboxEventUpdateDTO,
)
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.value_objects import (
    OutboxEventStatusEnum,
    OutboxEventTypeEnum,
    OrderStatusEnum,
    InboxEventStatusEnum,
)


log = logging.getLogger(__name__)


class ProcessInboxUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
    ):
        self._unit_of_work = unit_of_work

    def __call__(self):
        with self._unit_of_work as uow:
            events = uow.inbox_repo.get_pending(limit=10)
            if not events:
                return
            log.debug("Processing events: %s", events)

            for event in events:
                try:
                    uow.inbox_repo.mark_processed(
                        InboxEventUpdateDTO(
                            order_id=event.order_id,
                            event_type=event.event_type,
                            status=InboxEventStatusEnum.PROCESSED,
                        )
                    )
                    order = uow.order_repo.get_by_id(event.order_id)
                    if not order:
                        continue
                    uow.order_repo.update(
                        OrderUpdateDTO(
                            id=event.order_id,
                            status=OrderStatusEnum.from_event_type(event.event_type),
                        )
                    )
                    outbox_id = str(uuid4())
                    outbox_payload = {
                        "event_type": event.event_type.lower(),
                        "order_id": str(event.order_id),
                        "idempotency_key": outbox_id,
                    }
                    outbox_payload.update(event.payload)
                    uow.outbox_repo.create(
                        OutboxEventCreateDTO(
                            id=outbox_id,
                            order_id=event.order_id,
                            event_type=OutboxEventTypeEnum(event.event_type),
                            payload=outbox_payload,
                            status=OutboxEventStatusEnum.PENDING,
                        )
                    )
                except Exception as e:
                    log.error("Inbox message processing failed: %s", e)
            uow.commit()
