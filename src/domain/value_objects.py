from enum import StrEnum


class OrderStatusEnum(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class PaymentStatusEnum(StrEnum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
