from enum import StrEnum


class OrderStatusEnum(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

    @classmethod
    def from_payment_status(cls, payment_status: str) -> "OrderStatusEnum":
        mapping = {
            "succeeded": cls.PAID,
            "failed": cls.CANCELLED,
        }
        return mapping.get(payment_status)

    @classmethod
    def from_event_type(cls, event_type: str) -> "OrderStatusEnum":
        mapping = {
            "ORDER.CREATED": cls.NEW,
            "ORDER.PAID": cls.PAID,
            "ORDER.SHIPPED": cls.SHIPPED,
            "ORDER.CANCELLED": cls.CANCELLED,
        }
        return mapping.get(event_type.upper())


class PaymentStatusEnum(StrEnum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

    @classmethod
    def from_string(cls, value: str):
        upper_value = value.upper()
        if upper_value not in cls._value2member_map_:
            valid = ", ".join(cls._value2member_map_.keys())
            raise ValueError(f"'{value}' is not a valid status. Valid values: {valid}")
        return cls._value2member_map_[upper_value]


class OutboxEventStatusEnum(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class OutboxEventTypeEnum(StrEnum):
    CREATED = "ORDER.CREATED"
    PAID = "ORDER.PAID"
    SHIPPED = "ORDER.SHIPPED"
    CANCELLED = "ORDER.CANCELLED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

    @classmethod
    def from_payment_status(cls, payment_status: str) -> "OutboxEventTypeEnum":
        mapping = {
            "succeeded": cls.PAID,
            "failed": cls.CANCELLED,
        }
        return mapping.get(payment_status)


class InboxEventStatusEnum(StrEnum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class InboxEventTypeEnum(StrEnum):
    SHIPPED = "ORDER.SHIPPED"
    CANCELLED = "ORDER.CANCELLED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
