import logging
from dataclasses import asdict
from enum import Enum
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from src.application.dto import (
    OrderCreateDTO,
    OrderUpdateDTO,
    PaymentCreateDTO,
    PaymentUpdateDTO,
)
from src.domain.interfaces import (
    OrderRepository,
    PaymentRepository,
    OutboxRepository,
    InboxRepository,
)
from src.domain.models import (
    Order as OrderDomain,
    Payment as PaymentDomain,
    OutboxEvent,
    InboxEvent,
)
from src.domain.value_objects import OrderStatusEnum, PaymentStatusEnum
from src.infrastructure.orm.models import Order as OrderORM, Payment as PaymentORM


log = logging.getLogger(__name__)


def dto_to_orm_dict(dto) -> dict:
    data = asdict(dto)
    for key, value in data.items():
        if isinstance(value, Enum):
            data[key] = value.value
        elif isinstance(value, UUID):
            data[key] = str(value)
    return {k: v for k, v in data.items()}


class DjangoOrderRepository(OrderRepository):
    def _to_domain(self, orm_order: OrderORM) -> OrderDomain:
        return OrderDomain(
            id=orm_order.id,
            user_id=orm_order.user_id,
            quantity=orm_order.quantity,
            item_id=orm_order.item_id,
            status=OrderStatusEnum(orm_order.status),
            created_at=orm_order.created_at,
            update_at=orm_order.updated_at,
        )

    def _to_orm(self, dto: OrderCreateDTO | OrderUpdateDTO) -> dict:
        return dto_to_orm_dict(dto)

    def create(self, dto: OrderCreateDTO) -> OrderDomain:
        log.debug("Creating record for table: orders, with data: %s", dto)
        create_data = self._to_orm(dto)
        orm_order = OrderORM.objects.create(**create_data)
        return self._to_domain(orm_order)

    def get_by_id(self, order_id: UUID) -> OrderDomain:
        try:
            orm_order = OrderORM.objects.get(id=order_id)
        except ObjectDoesNotExist:
            raise ValueError(f"Order with id {order_id} not found")
        result = self._to_domain(orm_order)
        log.debug("Order id: %s, result: %s", order_id, result)
        return result

    def get_by_idempotency_key(self, idempotency_key: str) -> OrderDomain:
        try:
            orm_order = OrderORM.objects.get(idempotency_key=idempotency_key)
        except ObjectDoesNotExist:
            raise ValueError(f"Order with idempotency key {idempotency_key} not found")
        result = self._to_domain(orm_order)
        log.debug("Order with idempotency_key: %s, result: %s", idempotency_key, result)
        return result

    def update(self, dto: OrderUpdateDTO) -> OrderDomain:
        log.debug("Updating record for table: orders, with data: %s", dto)
        updated_count = OrderORM.objects.filter(id=dto.id).update(status=dto.status)
        if updated_count == 0:
            raise ValueError(f"Order with id {dto.id} not found")
        orm_order = OrderORM.objects.get(id=dto.id)
        return self._to_domain(orm_order)


class DjangoPaymentRepository(PaymentRepository):
    def _to_domain(self, orm_payment: PaymentORM) -> PaymentDomain:
        return PaymentDomain(
            id=orm_payment.id,
            user_id=orm_payment.user_id,
            order_id=orm_payment.order_id,
            amount=orm_payment.amount,
            status=PaymentStatusEnum(orm_payment.status),
            idempotency_key=orm_payment.idempotency_key,
            created_at=orm_payment.created_at,
            update_at=orm_payment.updated_at,
        )

    def _to_orm(self, dto: PaymentCreateDTO | PaymentUpdateDTO) -> dict:
        return dto_to_orm_dict(dto)

    def create(self, dto: PaymentCreateDTO) -> PaymentDomain:
        log.debug("Creating record for table: payments, with data: %s", dto)
        create_data = self._to_orm(dto)
        orm_payment = PaymentORM.objects.create(**create_data)
        return self._to_domain(orm_payment)

    def get_by_order(self, order_id: UUID) -> PaymentDomain:
        try:
            orm_payment = PaymentORM.objects.get(order_id=order_id)
        except ObjectDoesNotExist:
            raise ValueError(f"Payment for order {order_id} not found")
        result = self._to_domain(orm_payment)
        log.debug("Payment with order_id: %s, result: %s", order_id, result)
        return result

    def update(self, dto: PaymentUpdateDTO) -> PaymentDomain:
        log.debug("Updating record for table: payments, with data: %s", dto)
        updated_count = PaymentORM.objects.filter(id=dto.id).update(status=dto.status)
        if updated_count == 0:
            raise ValueError(f"Payment with id {dto.id} not found")
        orm_payment = PaymentORM.objects.get(id=dto.id)
        return self._to_domain(orm_payment)


class DjangoOutboxRepository(OutboxRepository):
    def create(self, event: OutboxEvent):
        pass

    def get_pending(self) -> OutboxEvent:
        pass

    def mark_published(self, event_id):
        pass


class DjangoInboxRepository(InboxRepository):
    def create(self, event: InboxEvent):
        pass

    def get_pending(self):
        pass

    def mark_processed(self, event_id):
        pass
