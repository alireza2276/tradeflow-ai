from rest_framework.routers import DefaultRouter

from apps.trade_orders.views import (
    CurrencyPurchaseViewSet,
    PaymentInstrumentViewSet,
    RegistrationOrderViewSet,
)

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

urlpatterns = router.urls