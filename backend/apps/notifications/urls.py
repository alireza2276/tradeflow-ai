from rest_framework.routers import DefaultRouter

from apps.notifications.views import NotificationLogViewSet


router = DefaultRouter()

router.register(
    "logs",
    NotificationLogViewSet,
    basename="notification-log",
)

urlpatterns = router.urls