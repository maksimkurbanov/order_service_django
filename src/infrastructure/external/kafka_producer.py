from typing import Any


import json

from src.application.ports.message_broker import MessageQueueProducer


class KafkaProducer(MessageQueueProducer):
    def __init__(self, bootstrap_servers: str, topic: str):
        from kafka import KafkaProducer as kp

        self._producer = kp(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
        )
        self._topic = topic

    def send(
        self,
        message: dict[str, Any],
        key: str,
        topic: str = None,
    ) -> None:
        target_topic = topic or self._topic
        future = self._producer.send(
            topic=target_topic,
            value=message,
            key=key,
        )
        future.get(timeout=10)

    def close(self):
        self._producer.close()
