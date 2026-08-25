import uuid

from django.db import models

from apps.trade_orders.models import CurrencyPurchase


class NotificationLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    currency_purchase = models.ForeignKey(
        CurrencyPurchase,
        on_delete=models.PROTECT,
        related_name="notification_logs",
    )

    notification_type = models.CharField(
        max_length=50,
    )

    sent_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "notification_logs"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "currency_purchase",
                    "notification_type",
                ],
                name="unique_notification_per_purchase",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "currency_purchase",
                    "notification_type",
                ],
                name="idx_notification_purchase_type",
            ),
        ]

    def __str__(self):
        return (
            f"{self.currency_purchase_id} - "
            f"{self.notification_type}"
        )
