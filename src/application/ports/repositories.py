from abc import ABC, abstractmethod

from src.domain.models import InboxEvent, OutboxEvent


class OutboxRepository(ABC):
    @abstractmethod
    def create(self, event) -> OutboxEvent:
        pass

    @abstractmethod
    def get_pending(self, limit: int) -> list[OutboxEvent]:
        pass

    @abstractmethod
    def mark_published(self, event) -> None:
        pass


class InboxRepository(ABC):
    @abstractmethod
    def create(self, event) -> InboxEvent:
        pass

    @abstractmethod
    def check_duplicate(self, event) -> InboxEvent | None:
        pass

    @abstractmethod
    def get_pending(self, limit: int) -> list[InboxEvent]:
        pass

    @abstractmethod
    def mark_processed(self, event_id) -> None:
        pass
