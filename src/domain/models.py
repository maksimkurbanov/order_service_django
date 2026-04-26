from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects import OrderStatusEnum, PaymentStatusEnum


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
    update_at: datetime


@dataclass
class Item:
    id: UUID
    name: str
    price: Decimal
    available_qty: int
    created_at: datetime
    updated_at: datetime


@dataclass
class OutboxEvent:
    pass


@dataclass
class InboxEvent:
    pass
