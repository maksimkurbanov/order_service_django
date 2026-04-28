from django.contrib import admin
from django.urls import path
from drf_spectacular.renderers import OpenApiJsonRenderer
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from src.interface.api.views import CreateOrderView, GetOrderView, PaymentCallbackView

urlpatterns = [
    path("admin", admin.site.urls),
    path(
        "openapi.json",
        SpectacularAPIView.as_view(renderer_classes=[OpenApiJsonRenderer]),
        name="schema",
    ),
    path("docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/orders", CreateOrderView.as_view(), name="create-order"),
    path(
        "api/orders/payment-callback",
        PaymentCallbackView.as_view(),
        name="payment-callback",
    ),
    path("api/orders/<str:order_id>", GetOrderView.as_view(), name="get-order"),
]
