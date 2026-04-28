from abc import ABC, abstractmethod
from typing import Any


class MessageQueueProducer(ABC):
    @abstractmethod
    def send(self, message: dict[str, Any], key: str, topic: str = None) -> None:
        pass


class MessageQueueConsumer(ABC):
    @abstractmethod
    def consume(self, timeout_ms: int) -> Any:
        pass

    @abstractmethod
    def consume_and_map(self, timeout_ms):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
