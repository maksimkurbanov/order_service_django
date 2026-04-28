from dependency_injector.wiring import inject, Provide
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from src.interface.serializers.orders import (
    CreateOrderRequestSerializer,
    OrderResponseSerializer,
    GetOrderPathParamSerializer,
)
from src.interface.container import Container
from src.interface.serializers.payments import (
    PaymentCallbackRequestSerializer,
    PaymentCallbackResponseSerializer,
)


class CreateOrderView(GenericAPIView):
    serializer_class = CreateOrderRequestSerializer

    @extend_schema(responses={status.HTTP_201_CREATED: OrderResponseSerializer})
    @inject
    def post(self, request, use_case=Provide[Container.create_order_use_case]):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        order = use_case(validated)
        response = OrderResponseSerializer(order)
        return Response(response.data, status=status.HTTP_201_CREATED)


class GetOrderView(GenericAPIView):
    serializer_class = GetOrderPathParamSerializer

    @extend_schema(responses={status.HTTP_200_OK: OrderResponseSerializer})
    @inject
    def get(self, request, order_id, use_case=Provide[Container.get_order_use_case]):
        serializer = self.get_serializer(data={"order_id": order_id})
        serializer.is_valid(raise_exception=True)
        validated_order_id = serializer.validated_data["order_id"]
        order = use_case(validated_order_id)
        response = OrderResponseSerializer(order)
        return Response(response.data, status=status.HTTP_200_OK)


class PaymentCallbackView(GenericAPIView):
    serializer_class = PaymentCallbackRequestSerializer

    @extend_schema(responses={status.HTTP_200_OK: PaymentCallbackResponseSerializer})
    @inject
    def post(
        self, request, use_case=Provide[Container.process_payment_callback_use_case]
    ):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        payment = use_case(validated)
        response = PaymentCallbackResponseSerializer(payment)
        return Response(response.data, status=status.HTTP_200_OK)
