import uuid
from decimal import Decimal

from django.db.models import UniqueConstraint, Q
from django.utils import timezone
from django.db import models

from src.domain.value_objects import (
    OrderStatusEnum,
    PaymentStatusEnum,
    OutboxEventStatusEnum,
    OutboxEventTypeEnum,
    InboxEventTypeEnum,
    InboxEventStatusEnum,
)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255)
    quantity = models.IntegerField()
    item_id = models.UUIDField()
    idempotency_key = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=OrderStatusEnum.choices())
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1), name="quantity_ge_1"
            )
        ]

    def __str__(self):
        return f"Order {self.id}"


class StringDecimalField(models.DecimalField):
    def __init__(self, max_digits=12, decimal_places=2, **kwargs):
        super().__init__(max_digits=max_digits, decimal_places=decimal_places, **kwargs)

    def from_db_value(self, value, expression, connection):
        """Convert database Decimal to a string when loading from DB."""
        if value is None:
            return None
        return f"{value:.2f}"

    def to_python(self, value):
        """Convert the Python value (could be string or Decimal) to string."""
        if value is None:
            return None
        if isinstance(value, str):
            # Validate and quantize to 2 decimal places
            dec = Decimal(value).quantize(Decimal("0.01"))
            return f"{dec:.2f}"
        if isinstance(value, Decimal):
            return f"{value:.2f}"
        raise ValueError(f"Expected string or Decimal, got {type(value)}")

    def get_prep_value(self, value):
        """Convert the string (or Decimal) to Decimal for database storage."""
        if value is None:
            return None
        if isinstance(value, str):
            return Decimal(value).quantize(Decimal("0.01"))
        if isinstance(value, (int, float, Decimal)):
            # Convert to Decimal with 2 decimal places
            return Decimal(str(value)).quantize(Decimal("0.01"))
        raise ValueError(f"Expected string or numeric, got {type(value)}")


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    user_id = models.UUIDField()
    order = models.OneToOneField(
        "Order", on_delete=models.CASCADE, related_name="payments", db_column="order_id"
    )
    amount = StringDecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatusEnum.choices())
    idempotency_key = models.UUIDField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"

    def __str__(self):
        return f"Payment {self.id} for Order {self.order_id}"


class Outbox(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        db_column="order_id",
        to_field="id",
    )
    event_type = models.CharField(choices=OutboxEventTypeEnum.choices())
    payload = models.JSONField(default=None)
    status = models.CharField(
        max_length=20,
        choices=OutboxEventStatusEnum.choices,
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "outbox"

        constraints = [
            UniqueConstraint(
                fields=["order", "event_type"],
                name="uq_outbox_order_event",
            ),
        ]

        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="ix_outbox_status_pending",
                condition=Q(status=OutboxEventStatusEnum.PENDING),
            ),
        ]


class Inbox(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    order_id = models.UUIDField()
    event_type = models.CharField(choices=InboxEventTypeEnum.choices())
    item_id = models.UUIDField()
    quantity = models.IntegerField()
    payload = models.JSONField(default=None)
    status = models.CharField(
        max_length=20,
        choices=OutboxEventStatusEnum.choices,
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inbox"

        constraints = [
            UniqueConstraint(
                fields=["order_id", "event_type"],
                name="uq_inbox_order_event",
            ),
        ]

        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="ix_inbox_status_pending",
                condition=Q(status=InboxEventStatusEnum.PENDING),
            ),
        ]
