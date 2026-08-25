from rest_framework.routers import DefaultRouter

from apps.trade_orders.views import (
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

urlpatterns = router.urls