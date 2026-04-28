from datetime import datetime
from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects import (
    OrderStatusEnum,
    PaymentStatusEnum,
    OutboxEventTypeEnum,
    OutboxEventStatusEnum,
    InboxEventTypeEnum,
    InboxEventStatusEnum,
)


@dataclass
class Order:
    id: UUID
    user_id: str
    quantity: int
    item_id: UUID
    status: OrderStatusEnum
    created_at: datetime
    update_at: datetime


@dataclass
class Payment:
    id: UUID
    user_id: UUID
    order_id: UUID
    amount: str
    status: PaymentStatusEnum
    idempotency_key: str | UUID
    created_at: datetime
    updated_at: datetime


@dataclass
class Item:
    id: UUID
    name: str
    price: str
    available_qty: int
    created_at: datetime
    updated_at: datetime


@dataclass
class OutboxEvent:
    id: UUID
    order_id: UUID
    event_type: OutboxEventTypeEnum
    payload: dict
    status: OutboxEventStatusEnum
    created_at: datetime
    updated_at: datetime


@dataclass
class InboxEvent:
    id: UUID
    order_id: UUID
    event_type: InboxEventTypeEnum
    payload: dict
    status: InboxEventStatusEnum
    created_at: datetime
    updated_at: datetime
