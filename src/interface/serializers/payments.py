import rest_framework.serializers as s

from src.domain.value_objects import PaymentStatusEnum


class PaymentCallbackRequestSerializer(s.Serializer):
    payment_id = s.UUIDField(required=True)
    order_id = s.UUIDField(required=True)
    status = s.ChoiceField(
        required=True,
        choices=[choice[0].lower() for choice in PaymentStatusEnum.choices()],
    )
    amount = s.CharField(required=True)
    error_message = s.CharField(required=True, allow_null=True)


class PaymentCallbackResponseSerializer(s.Serializer):
    id = s.UUIDField()
    user_id = s.UUIDField()
    order_id = s.UUIDField()
    amount = s.CharField()
    status = s.ChoiceField(choices=PaymentStatusEnum.choices())
    idempotency_key = s.CharField()
    created_at = s.DateTimeField()
    updated_at = s.DateTimeField()
