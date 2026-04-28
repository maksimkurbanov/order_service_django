from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal

from src.domain.value_objects import (
    OrderStatusEnum,
    PaymentStatusEnum,
    OutboxEventTypeEnum,
    OutboxEventStatusEnum,
    InboxEventTypeEnum,
    InboxEventStatusEnum,
)


@dataclass
class OrderCreateDTO:
    user_id: str
    quantity: int
    item_id: UUID
    status: OrderStatusEnum = OrderStatusEnum.NEW
    idempotency_key: str | UUID = None

    def __post_init__(self):
        if isinstance(self.idempotency_key, UUID):
            self.idempotency_key = str(self.idempotency_key)
        if self.quantity < 1:
            raise ValueError("quantity must be >= 1")


@dataclass
class OrderUpdateDTO:
    id: UUID
    status: OrderStatusEnum


@dataclass
class PaymentCreateDTO:
    id: UUID
    user_id: UUID
    order_id: UUID
    amount: str
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING
    idempotency_key: UUID | str = None

    def __post_init__(self):
        if isinstance(self.idempotency_key, UUID):
            self.idempotency_key = str(self.idempotency_key)
        try:
            Decimal(self.amount).quantize(Decimal("0.01"))
        except Exception as e:
            raise ValueError(f"Invalid amount: {e}")
        if isinstance(self.status, str) and not isinstance(
            self.status, PaymentStatusEnum
        ):
            self.status = PaymentStatusEnum.from_string(self.status)


@dataclass
class PaymentUpdateDTO:
    id: UUID
    status: PaymentStatusEnum


@dataclass
class OutboxEventCreateDTO:
    id: str
    order_id: UUID
    event_type: OutboxEventTypeEnum
    payload: dict
    status: OutboxEventStatusEnum


@dataclass
class OutboxEventUpdateDTO:
    order_id: UUID
    event_type: OutboxEventTypeEnum
    status: OutboxEventStatusEnum


@dataclass
class InboxEventCreateDTO:
    id: UUID
    event_type: str
    order_id: UUID
    item_id: UUID
    quantity: int
    payload: dict
    status: InboxEventStatusEnum


@dataclass
class InboxEventUpdateDTO:
    order_id: UUID
    event_type: InboxEventTypeEnum
    status: InboxEventStatusEnum
