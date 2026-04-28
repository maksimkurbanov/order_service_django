import json
import logging

from kafka.consumer.fetcher import ConsumerRecord

from src.application.ports.message_broker import MessageQueueConsumer
from src.infrastructure.inbox_mapper import message_to_inbox_dto

log = logging.getLogger(__name__)


class KafkaConsumer(MessageQueueConsumer):
    def __init__(
        self, bootstrap_servers: str, topic: str, group_id: str = None
    ) -> None:
        from kafka import KafkaConsumer as KConsumer

        self._topic = topic
        self._consumer = KConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            enable_auto_commit=False,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            auto_offset_reset="earliest",
            group_id=group_id,
        )

    def consume(self, timeout_ms: int = 1000) -> ConsumerRecord | None:
        response = self._consumer.poll(timeout_ms=timeout_ms, max_records=1)
        if not response:
            return None
        return list(response.values())[0][0]

    def consume_and_map(self, timeout_ms: int = 1000) -> dict | None:
        record = self.consume(timeout_ms)
        if record is None:
            return None
        return message_to_inbox_dto(record.value)

    def close(self) -> None:
        self._consumer.close()

    def commit(self) -> None:
        self._consumer.commit()

    def __enter__(self) -> "KafkaConsumer":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
