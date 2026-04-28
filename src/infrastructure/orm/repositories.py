import logging
from dataclasses import asdict
from enum import Enum
from uuid import UUID

from django.utils import timezone

from src.application.dto import (
    OrderCreateDTO,
    OrderUpdateDTO,
    PaymentCreateDTO,
    PaymentUpdateDTO,
    OutboxEventCreateDTO,
    OutboxEventUpdateDTO,
    InboxEventCreateDTO,
    InboxEventUpdateDTO,
)
from src.application.ports.repositories import OutboxRepository, InboxRepository
from src.domain.interfaces import (
    OrderRepository,
    PaymentRepository,
)
from src.domain.models import (
    Order as OrderDomain,
    Payment as PaymentDomain,
    OutboxEvent as OutboxEventDomain,
    InboxEvent as InboxEventDomain,
)
from src.domain.value_objects import (
    OrderStatusEnum,
    PaymentStatusEnum,
    OutboxEventTypeEnum,
    OutboxEventStatusEnum,
    InboxEventTypeEnum,
    InboxEventStatusEnum,
)
from src.infrastructure.orm.models import (
    Order as OrderORM,
    Payment as PaymentORM,
    Outbox as OutboxEventORM,
    Inbox as InboxEventORM,
)


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

    def get_by_id(self, order_id: UUID) -> OrderDomain | None:
        orm_order = OrderORM.objects.filter(id=order_id).first()
        if not orm_order:
            return None
        result = self._to_domain(orm_order)
        log.debug("Order id: %s, result: %s", order_id, result)
        return result

    def get_by_idempotency_key(self, idempotency_key: str) -> OrderDomain | None:
        orm_order = OrderORM.objects.filter(idempotency_key=idempotency_key).first()
        if not orm_order:
            return None
        result = self._to_domain(orm_order)
        log.debug("Order with idempotency_key: %s, result: %s", idempotency_key, result)
        return result

    def update(self, dto: OrderUpdateDTO) -> OrderDomain:
        log.debug("Updating record for table: orders, with data: %s", dto)
        updated_count = OrderORM.objects.filter(id=dto.id).update(
            status=dto.status, updated_at=timezone.now()
        )
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
            updated_at=orm_payment.updated_at,
        )

    def _to_orm(self, dto: PaymentCreateDTO | PaymentUpdateDTO) -> dict:
        return dto_to_orm_dict(dto)

    def create(self, dto: PaymentCreateDTO) -> PaymentDomain:
        log.debug("Creating record for table: payments, with data: %s", dto)
        create_data = self._to_orm(dto)
        orm_payment = PaymentORM.objects.create(**create_data)
        return self._to_domain(orm_payment)

    def get_by_order(self, order_id: UUID) -> PaymentDomain | None:
        orm_payment = PaymentORM.objects.filter(order_id=order_id).first()
        if not orm_payment:
            return None
        result = self._to_domain(orm_payment)
        log.debug("Payment with order_id: %s, result: %s", order_id, result)
        return result

    def update(self, dto: PaymentUpdateDTO) -> PaymentDomain:
        log.debug("Updating record for table: payments, with data: %s", dto)
        updated_count = PaymentORM.objects.filter(id=dto.id).update(
            status=dto.status, updated_at=timezone.now()
        )
        if updated_count == 0:
            raise ValueError(f"Payment with id {dto.id} not found")
        orm_payment = PaymentORM.objects.get(id=dto.id)
        return self._to_domain(orm_payment)


class DjangoOutboxRepository(OutboxRepository):
    def _to_domain(self, orm_outbox: OutboxEventORM) -> OutboxEventDomain:
        return OutboxEventDomain(
            id=orm_outbox.id,
            order_id=orm_outbox.order_id,
            event_type=OutboxEventTypeEnum(orm_outbox.event_type),
            payload=orm_outbox.payload,
            status=OutboxEventStatusEnum(orm_outbox.status),
            created_at=orm_outbox.created_at,
            updated_at=orm_outbox.updated_at,
        )

    def _to_orm(self, dto: OutboxEventCreateDTO) -> dict:
        return dto_to_orm_dict(dto)

    def create(self, dto: OutboxEventCreateDTO) -> OutboxEventDomain:
        log.debug("Creating record for table: outbox, with data: %s", dto)
        create_data = self._to_orm(dto)
        orm_outbox = OutboxEventORM.objects.create(**create_data)
        return self._to_domain(orm_outbox)

    def get_pending(self, limit: int = 10) -> list[OutboxEventDomain]:
        qs = (
            OutboxEventORM.objects.filter(status=OutboxEventStatusEnum.PENDING)
            .order_by("created_at")
            .select_for_update(skip_locked=True)[:limit]
        )
        locked_records = list(qs)
        return [self._to_domain(record) for record in locked_records]

    def mark_published(self, dto: OutboxEventUpdateDTO) -> None:
        log.debug(
            "Marking Outbox event with order id: %s, event_type: %s as published",
            dto.order_id,
            dto.event_type,
        )
        updated_count = OutboxEventORM.objects.filter(
            order_id=dto.order_id, event_type=dto.event_type
        ).update(status=dto.status, updated_at=timezone.now())
        if updated_count == 0:
            raise ValueError(
                f"Outbox event with order_id: {dto.order_id}, event_type: {dto.event_type} not found"
            )


class DjangoInboxRepository(InboxRepository):
    def _to_domain(self, orm_inbox: InboxEventORM) -> InboxEventDomain:
        return InboxEventDomain(
            id=orm_inbox.id,
            order_id=orm_inbox.order_id,
            event_type=InboxEventTypeEnum(orm_inbox.event_type),
            payload=orm_inbox.payload,
            status=InboxEventStatusEnum(orm_inbox.status),
            created_at=orm_inbox.created_at,
            updated_at=orm_inbox.updated_at,
        )

    def _to_orm(self, dto: InboxEventCreateDTO) -> dict:
        return dto_to_orm_dict(dto)

    def create(self, dto: InboxEventCreateDTO):
        log.debug("Creating record for table: inbox, with data: %s", dto)
        create_data = self._to_orm(dto)
        orm_inbox = InboxEventORM.objects.create(**create_data)
        return self._to_domain(orm_inbox)

    def check_duplicate(self, dto: dict) -> InboxEventORM | None:
        qs = InboxEventORM.objects.filter(
            order_id=UUID(dto["order_id"]), event_type=dto["event_type"]
        )
        duplicate = qs.first()
        log.debug("Duplicate records: %s", duplicate)
        return duplicate

    def get_pending(self, limit: int = 10) -> list[InboxEventDomain]:
        qs = (
            InboxEventORM.objects.filter(status=InboxEventStatusEnum.PENDING)
            .order_by("created_at")
            .select_for_update(skip_locked=True)[:limit]
        )
        locked_records = list(qs)
        return [self._to_domain(record) for record in locked_records]

    def mark_processed(self, dto: InboxEventUpdateDTO):
        log.debug(
            "Marking Inbox event with order id: %s, event_type: %s as processed",
            dto.order_id,
            dto.event_type,
        )
        updated_count = InboxEventORM.objects.filter(
            order_id=dto.order_id, event_type=dto.event_type
        ).update(status=dto.status, updated_at=timezone.now())
        if updated_count == 0:
            raise ValueError(
                f"Inbox event with order_id: {dto.order_id}, event_type: {dto.event_type} not found"
            )
