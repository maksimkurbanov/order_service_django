from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects import OrderStatusEnum, PaymentStatusEnum


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
            from decimal import Decimal

            Decimal(self.amount).quantize(Decimal("0.01"))
        except Exception as e:
            raise ValueError(f"Invalid amount: {e}")


@dataclass
class PaymentUpdateDTO:
    id: UUID
    status: PaymentStatusEnum
