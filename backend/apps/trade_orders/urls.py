from rest_framework.routers import DefaultRouter

from apps.trade_orders.views import RegistrationOrderViewSet


router = DefaultRouter()

router.register(
    "registration-orders",
    RegistrationOrderViewSet,
    basename="registration-order",
)

urlpatterns = router.urls