import uuid

from django.db import models

from apps.companies.models import Company

from django.conf import settings

class RegistrationOrder(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="registration_orders",
    )

    order_number = models.CharField(
        max_length=50,
    )

    registered_amount = models.DecimalField(
        max_digits=20,
        decimal_places=4,
    )

    currency = models.CharField(
        max_length=3,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "registration_orders"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "order_number"],
                name="unique_order_number_per_company",
            ),
        ]
        indexes = [
            models.Index(
                fields=["company", "is_active"],
                name="idx_order_company_active",
            ),
        ]

    def __str__(self):
        return f"{self.order_number} - {self.company.name}"

class PaymentInstrument(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    registration_order = models.OneToOneField(
        RegistrationOrder,
        on_delete=models.PROTECT,
        related_name="payment_instrument",
    )

    instrument_number = models.CharField(
        max_length=100,
        unique=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "payment_instruments"

    def __str__(self):
        return self.instrument_number

class CurrencyPurchase(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    registration_order = models.ForeignKey(
        RegistrationOrder,
        on_delete=models.PROTECT,
        related_name="currency_purchases",
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=4,
    )

    currency = models.CharField(
        max_length=3,
    )

    purchase_date = models.DateField()

    deadline = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    is_void = models.BooleanField(
        default=False,
        db_index=True,
    )

    voided_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="voided_currency_purchases",
    )

    void_reason = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "currency_purchases"
        ordering = ["purchase_date"]
        constraints = [
            models.CheckConstraint(
                condition=(
                        models.Q(
                            is_void=False,
                            voided_at__isnull=True,
                            voided_by__isnull=True,
                            void_reason="",
                        )
                        |
                        (
                                models.Q(
                                    is_void=True,
                                    voided_at__isnull=False,
                                    voided_by__isnull=False,
                                )
                                & ~models.Q(void_reason="")
                        )
                ),
                name="currency_purchase_void_state_consistent",
            ),
        ]

        permissions = [
            (
                "void_currencypurchase",
                "Can submit currency purchase void request",
            ),
        ]



    def __str__(self):
        return (
            f"{self.amount} {self.currency} "
            f"- {self.purchase_date}"
        )

class ShipmentPart(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    currency_purchase = models.ForeignKey(
        CurrencyPurchase,
        on_delete=models.PROTECT,
        related_name="shipment_parts",
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=4,
    )

    shipment_date = models.DateField(
        null=True,
        blank=True,
    )

    received_date = models.DateField(
        null=True,
        blank=True,
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    is_void = models.BooleanField(
        default=False,
        db_index=True,
    )

    voided_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="voided_shipment_parts",
    )

    void_reason = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "shipment_parts"
        ordering = ["-received_date", "-created_at"]
        indexes = [
            models.Index(
                fields=["currency_purchase", "received_date"],
                name="idx_shipment_purchase_received",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                        models.Q(
                            is_void=False,
                            voided_at__isnull=True,
                            voided_by__isnull=True,
                            void_reason="",
                        )
                        |
                        (
                                models.Q(
                                    is_void=True,
                                    voided_at__isnull=False,
                                    voided_by__isnull=False,
                                )
                                & ~models.Q(void_reason="")
                        )
                ),
                name="shipment_part_void_state_consistent",
            ),
        ]

        permissions = [
            (
                "void_shipmentpart",
                "Can submit shipment part void request",
            ),
        ]

    def __str__(self):
        return (
            f"{self.amount} {self.currency_purchase.currency} "
            f"- {self.reference_number or 'No reference'}"
        )
