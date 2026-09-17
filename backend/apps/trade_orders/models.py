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

    activity_type = models.CharField(
        max_length=20,
        choices=Company.CompanyType.choices,
        null=True,
        blank=True,
        help_text=(
            "Snapshot of the activity type recorded on the registration "
            "order. Regulatory deadlines must use this value rather than "
            "the company's current master-data type."
        ),
    )

    shipment_deadline_months = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Maximum shipping-document deadline applicable to this "
            "registration order under the current CBI rule/table."
        ),
    )

    regulatory_rule_reference = models.CharField(
        max_length=120,
        blank=True,
        help_text="CBI circular / Part One / table or clause reference.",
    )

    goods_category_code = models.CharField(
        max_length=80,
        blank=True,
        db_index=True,
        help_text=(
            "Internal regulatory goods-category code. Keep this code aligned "
            "with the verified regulatory matrix; blank means unclassified."
        ),
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

    class OperationType(models.TextChoices):
        REMITTANCE = "REMITTANCE", "FX Remittance"
        DOCUMENTARY_COLLECTION = "DOCUMENTARY_COLLECTION", "Documentary Collection"
        LETTER_OF_CREDIT = "LETTER_OF_CREDIT", "Letter of Credit"
        OTHER = "OTHER", "Other"

    operation_type = models.CharField(
        max_length=40,
        choices=OperationType.choices,
        default=OperationType.REMITTANCE,
        db_index=True,
    )

    issue_date = models.DateField(
        null=True,
        blank=True,
        help_text="Issue/opening/registration date of the payment instrument.",
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

    purchase_date = models.DateField(
        help_text="Currency funding/purchase date.",
    )

    remittance_date = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Actual remittance issue date. Required only when a selected "
            "regulatory rule uses REMITTANCE_DATE as its basis."
        ),
    )

    funding_source_code = models.CharField(
        max_length=80,
        blank=True,
        db_index=True,
        help_text=(
            "Internal code for the FX funding/source category used by the "
            "verified regulatory matrix."
        ),
    )

    original_deadline = models.DateField(
        null=True,
        blank=True,
    )

    deadline = models.DateField()

    deadline_extension_reference = models.CharField(
        max_length=120,
        blank=True,
    )

    deadline_extension_reason = models.TextField(
        blank=True,
    )

    applied_rule = models.ForeignKey(
        "RegulatoryRule",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="currency_purchases",
    )

    class ObligationStatus(models.TextChoices):
        OPEN = "OPEN", "Open"
        DOCUMENTS_COMPLETE = "DOCUMENTS_COMPLETE", "Documents complete"
        CLEARANCE_PENDING = "CLEARANCE_PENDING", "Clearance pending"
        PARTIALLY_CLEARED = "PARTIALLY_CLEARED", "Partially cleared"
        CLEARED = "CLEARED", "Cleared"
        SETTLED = "SETTLED", "FX obligation settled"
        OVERDUE = "OVERDUE", "Overdue"

    obligation_status = models.CharField(
        max_length=30,
        choices=ObligationStatus.choices,
        default=ObligationStatus.OPEN,
        db_index=True,
    )

    obligation_settled_at = models.DateTimeField(
        null=True,
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


class RegulatoryRule(models.Model):
    class DeadlineBasis(models.TextChoices):
        PURCHASE_DATE = "PURCHASE_DATE", "Currency funding/purchase date"
        REMITTANCE_DATE = "REMITTANCE_DATE", "Remittance date"
        INSTRUMENT_DATE = "INSTRUMENT_DATE", "Payment instrument date"

    class DeadlineKind(models.TextChoices):
        IMPORT_CLEARANCE = "IMPORT_CLEARANCE", "Import/clearance deadline"
        SHIPPING_DOCUMENTS = "SHIPPING_DOCUMENTS", "Shipping-document deadline"
        FX_DIFFERENCE = "FX_DIFFERENCE", "FX-difference deadline"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=80, unique=True)
    operation_type = models.CharField(max_length=40, choices=PaymentInstrument.OperationType.choices, db_index=True)
    activity_type = models.CharField(max_length=20, choices=Company.CompanyType.choices, null=True, blank=True, db_index=True)
    goods_category_code = models.CharField(max_length=80, blank=True, db_index=True)
    funding_source_code = models.CharField(max_length=80, blank=True, db_index=True)
    deadline_kind = models.CharField(max_length=40, choices=DeadlineKind.choices, default=DeadlineKind.IMPORT_CLEARANCE)
    deadline_basis = models.CharField(max_length=30, choices=DeadlineBasis.choices)
    deadline_months = models.PositiveSmallIntegerField(null=True, blank=True)
    deadline_days = models.PositiveSmallIntegerField(null=True, blank=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    priority = models.PositiveSmallIntegerField(default=100)
    is_active = models.BooleanField(default=True, db_index=True)
    internal_reference = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "regulatory_rules"
        ordering = ["priority", "-effective_from", "code"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (models.Q(deadline_months__isnull=False) & models.Q(deadline_days__isnull=True))
                    | (models.Q(deadline_months__isnull=True) & models.Q(deadline_days__isnull=False))
                ),
                name="regulatory_rule_exactly_one_duration",
            ),
        ]

    def __str__(self):
        return self.code


class RegulatoryDeadline(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency_purchase = models.ForeignKey(
        CurrencyPurchase,
        on_delete=models.PROTECT,
        related_name="regulatory_deadlines",
    )
    deadline_kind = models.CharField(
        max_length=40,
        choices=RegulatoryRule.DeadlineKind.choices,
        db_index=True,
    )
    applied_rule = models.ForeignKey(
        RegulatoryRule,
        on_delete=models.PROTECT,
        related_name="regulatory_deadlines",
        null=True,
        blank=True,
    )
    basis_date = models.DateField()
    original_deadline = models.DateField()
    effective_deadline = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "regulatory_deadlines"
        ordering = ["effective_deadline", "deadline_kind"]
        constraints = [
            models.UniqueConstraint(
                fields=["currency_purchase", "deadline_kind"],
                name="unique_deadline_kind_per_purchase",
            ),
            models.CheckConstraint(
                condition=models.Q(effective_deadline__gte=models.F("original_deadline")),
                name="reg_deadline_effective_gte_original",
            ),
        ]

    def __str__(self):
        return f"{self.currency_purchase_id} - {self.deadline_kind}"


class DeadlineExtension(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency_purchase = models.ForeignKey(CurrencyPurchase, on_delete=models.PROTECT, related_name="deadline_extensions")
    regulatory_deadline = models.ForeignKey(
        RegulatoryDeadline,
        on_delete=models.PROTECT,
        related_name="extensions",
        null=True,
        blank=True,
    )
    previous_deadline = models.DateField()
    new_deadline = models.DateField()
    reason = models.TextField()
    reference = models.CharField(max_length=160, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approved_deadline_extensions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "deadline_extensions"
        ordering = ["created_at"]
        permissions = [("extend_currencypurchase_deadline", "Can extend currency purchase deadline")]
        constraints = [models.CheckConstraint(condition=models.Q(new_deadline__gt=models.F("previous_deadline")), name="deadline_extension_moves_forward")]


class CustomsClearance(models.Model):
    class Status(models.TextChoices):
        DECLARED = "DECLARED", "Declared"
        PARTIAL = "PARTIAL", "Partially cleared"
        FINAL = "FINAL", "Final clearance"
        REJECTED = "REJECTED", "Rejected/invalid"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency_purchase = models.ForeignKey(CurrencyPurchase, on_delete=models.PROTECT, related_name="customs_clearances")
    declaration_number = models.CharField(max_length=100)
    clearance_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DECLARED, db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customs_clearances"
        ordering = ["-clearance_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["currency_purchase", "declaration_number"], name="unique_clearance_per_purchase_declaration"),
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="customs_clearance_amount_positive"),
        ]

    def __str__(self):
        return self.declaration_number
