import time
import random
import logging


from src.application.dto import OutboxEventUpdateDTO
from src.application.ports.message_broker import MessageQueueProducer
from src.application.ports.unit_of_work import UnitOfWork
from src.application.ports.services import NotificationService
from src.domain.value_objects import (
    OutboxEventStatusEnum,
    OutboxEventTypeEnum,
    OrderStatusEnum,
)


log = logging.getLogger(__name__)


class ProcessOutboxUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        event_publisher: MessageQueueProducer,
        notification_service: NotificationService,
        max_retries: int,
    ):
        self._unit_of_work = unit_of_work
        self._event_publisher = event_publisher
        self._notification_service = notification_service
        self._max_retries = int(max_retries)

    def __call__(self):
        with self._unit_of_work as uow:
            events = uow.outbox_repo.get_pending(limit=5)
            if not events:
                return
            log.debug("Processing events: %s", events)

            for event in events:
                for attempt in range(1, self._max_retries + 1):
                    try:
                        if event.event_type == OutboxEventTypeEnum.PAID:
                            self._event_publisher.send(
                                message=event.payload, key=str(event.order_id)
                            )

                        self._notification_service.send_notification(
                            status=OrderStatusEnum.from_event_type(event.event_type),
                            order_id=event.order_id,
                            idempotency_key=event.id,
                        )
                        uow.outbox_repo.mark_published(
                            OutboxEventUpdateDTO(
                                order_id=event.order_id,
                                event_type=event.event_type,
                                status=OutboxEventStatusEnum.SENT,
                            )
                        )
                        break
                    except Exception as e:
                        log.warning(
                            "Attempt %d/%d failed for event %s %s: %s",
                            attempt,
                            self._max_retries,
                            event.order_id,
                            event.event_type,
                            e,
                        )
                        if attempt == self._max_retries:
                            log.error(
                                "All retries exhausted for event %s %s",
                                event.order_id,
                                event.event_type,
                            )
                        else:
                            delay = 2 ** (attempt - 1) + random.uniform(0, 1)
                            time.sleep(delay)
            uow.commit()
