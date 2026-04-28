import logging
import uuid

from src.application.dto import InboxEventCreateDTO
from src.application.ports.message_broker import MessageQueueConsumer
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.value_objects import InboxEventStatusEnum

log = logging.getLogger(__name__)


class WriteToInboxUseCase:
    def __init__(
        self, unit_of_work: UnitOfWork, consumer: MessageQueueConsumer
    ) -> None:
        self._unit_of_work = unit_of_work
        self._consumer = consumer

    def __call__(self) -> None:
        try:
            message = self._consumer.consume_and_map(timeout_ms=5000)
            if not message:
                return

            log.info("Handling incoming message: %s", message)

            with self._unit_of_work as uow:
                duplicate = uow.inbox_repo.check_duplicate(message)
                if not duplicate:
                    uow.inbox_repo.create(
                        InboxEventCreateDTO(
                            id=uuid.uuid4(),
                            status=InboxEventStatusEnum.PENDING,
                            **message,
                        )
                    )
                uow.commit()
            self._consumer.commit()
        except Exception as e:
            log.error("Error occurred while handling incoming message: %s", e)
