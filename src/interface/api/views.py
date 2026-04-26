from dependency_injector.wiring import inject, Provide
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.interface.serializers.orders import (
    CreateOrderRequestSerializer,
    OrderResponseSerializer,
    GetOrderPathParamSerializer,
)
from src.interface.container import Container


class CreateOrderView(APIView):
    @inject
    def post(self, request, use_case=Provide[Container.create_order_use_case]):
        serializer = CreateOrderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        order = use_case(validated)
        response = OrderResponseSerializer(order)
        return Response(response.data, status=status.HTTP_201_CREATED)


class GetOrderView(APIView):
    @inject
    def get(self, request, order_id, use_case=Provide[Container.get_order_use_case]):
        param_serializer = GetOrderPathParamSerializer(data={"order_id": order_id})
        param_serializer.is_valid(raise_exception=True)
        validated_order_id = param_serializer.validated_data["order_id"]
        order = use_case(validated_order_id)
        serializer = OrderResponseSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
