import rest_framework.serializers as s

from src.domain.value_objects import OrderStatusEnum


class CreateOrderRequestSerializer(s.Serializer):
    user_id = s.CharField(required=True)
    quantity = s.IntegerField(min_value=1, required=True)
    item_id = s.UUIDField(required=True)
    idempotency_key = s.CharField(required=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance.status, "value"):
            data["status"] = instance.status.value
        return data


class GetOrderPathParamSerializer(s.Serializer):
    order_id = s.UUIDField(required=True)

    def validate_order_id(self, value):
        return value


class OrderResponseSerializer(s.Serializer):
    id = s.UUIDField()
    user_id = s.CharField()
    quantity = s.IntegerField()
    item_id = s.UUIDField()
    status = s.ChoiceField(choices=OrderStatusEnum.choices())
    created_at = s.DateTimeField()
    update_at = s.DateTimeField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance.status, "value"):
            data["status"] = instance.status.value
        return data
