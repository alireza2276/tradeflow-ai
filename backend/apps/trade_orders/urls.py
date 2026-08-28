from rest_framework.routers import DefaultRouter

from apps.trade_orders.views import (
    RegistrationOrderViewSet,
    PaymentInstrumentViewSet,
    CurrencyPurchaseViewSet,
    ShipmentPartViewSet,
    DashboardSummaryAPIView,
)

from django.urls import path


router = DefaultRouter()

router.register(
    "registration-orders",
    RegistrationOrderViewSet,
    basename="registration-order",
)

router.register(
    "payment-instruments",
    PaymentInstrumentViewSet,
    basename="payment-instrument",
)

router.register(
    "currency-purchases",
    CurrencyPurchaseViewSet,
    basename="currency-purchase",
)

router.register(
    "shipment-parts",
    ShipmentPartViewSet,
    basename="shipment-part",
)

urlpatterns = router.urls

urlpatterns += [
    path(
        "dashboard/",
        DashboardSummaryAPIView.as_view(),
        name="dashboard-summary",
    ),
]