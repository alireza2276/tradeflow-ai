import uuid

from django.conf import settings
from django.db import models

from apps.companies.models import Company
from apps.trade_orders.models import CurrencyPurchase


class NotificationRecipient(models.Model):
    """Configurable destination for bank users and company contacts.

    BANK_USER rows may optionally point to a Django user. COMPANY_CONTACT rows
    must point to a company. Phone numbers are configuration data, not embedded
    in notification rules.
    """

    class RecipientType(models.TextChoices):
        BANK_USER = "BANK_USER", "Bank user"
        COMPANY_CONTACT = "COMPANY_CONTACT", "Company contact"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_type = models.CharField(max_length=30, choices=RecipientType.choices, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="notification_recipients",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="notification_recipients",
    )
    display_name = models.CharField(max_length=160)
    phone_number = models.CharField(max_length=30, blank=True)
    in_app_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_recipients"
        indexes = [
            models.Index(fields=["recipient_type", "is_active"], name="notif_recip_ty_act_idx"),
            models.Index(fields=["company", "is_active"], name="idx_notif_recipient_company"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(recipient_type="BANK_USER", company__isnull=True)
                    | models.Q(recipient_type="COMPANY_CONTACT", company__isnull=False, user__isnull=True)
                ),
                name="notification_recipient_scope_valid",
            ),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.recipient_type})"


class NotificationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency_purchase = models.ForeignKey(
        CurrencyPurchase,
        on_delete=models.PROTECT,
        related_name="notification_logs",
    )
    notification_type = models.CharField(max_length=80)
    deadline_kind = models.CharField(max_length=40, blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Compatibility with the old API/UI name.
    @property
    def sent_at(self):
        return self.created_at

    class Meta:
        db_table = "notification_logs"
        constraints = [
            models.UniqueConstraint(
                fields=["currency_purchase", "notification_type", "deadline_kind", "deadline_date"],
                name="unique_notification_event_per_deadline",
            ),
        ]
        indexes = [
            models.Index(
                fields=["currency_purchase", "notification_type"],
                name="idx_notification_purchase_type",
            ),
            models.Index(fields=["deadline_date", "notification_type"], name="idx_notification_deadline_type"),
        ]

    def __str__(self):
        return f"{self.currency_purchase_id} - {self.notification_type}"


class NotificationDelivery(models.Model):
    class Channel(models.TextChoices):
        IN_APP = "IN_APP", "In app"
        SMS = "SMS", "SMS"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"
        SKIPPED = "SKIPPED", "Skipped"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        NotificationLog,
        on_delete=models.PROTECT,
        related_name="deliveries",
    )
    recipient = models.ForeignKey(
        NotificationRecipient,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="deliveries",
    )
    channel = models.CharField(max_length=20, choices=Channel.choices)
    destination = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    provider = models.CharField(max_length=60, blank=True)
    provider_message_id = models.CharField(max_length=160, blank=True)
    error_message = models.TextField(blank=True)
    attempted_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notification_deliveries"
        constraints = [
            models.UniqueConstraint(
                fields=["notification", "recipient", "channel"],
                name="unique_notification_delivery_recipient_channel",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "channel"], name="notif_deliv_st_ch_idx"),
        ]

    def __str__(self):
        return f"{self.notification_id} - {self.channel} - {self.status}"
