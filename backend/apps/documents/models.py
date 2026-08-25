import uuid

from django.core.validators import MinValueValidator
from django.db import models

from apps.trade_orders.models import ShipmentPart


class Invoice(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    shipment_part = models.OneToOneField(
        ShipmentPart,
        on_delete=models.PROTECT,
        related_name="invoice",
    )

    fob_amount = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        validators=[MinValueValidator(0)],
    )

    freight_amount = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0)],
    )

    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        editable=False,
    )

    submission_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "invoices"
        ordering = ["-submission_date"]

    def save(self, *args, **kwargs):
        self.total_amount = self.fob_amount + self.freight_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice - {self.shipment_part.reference_number or self.id}"
