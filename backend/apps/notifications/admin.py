from django.contrib import admin

from apps.notifications.models import NotificationDelivery, NotificationLog, NotificationRecipient


@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    list_display = ("display_name", "recipient_type", "company", "phone_number", "in_app_enabled", "sms_enabled", "is_active")
    list_filter = ("recipient_type", "in_app_enabled", "sms_enabled", "is_active")
    search_fields = ("display_name", "phone_number", "company__name", "user__username")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("currency_purchase", "notification_type", "deadline_kind", "deadline_date", "created_at")
    list_filter = ("notification_type", "deadline_kind", "created_at")
    readonly_fields = ("id", "currency_purchase", "notification_type", "deadline_kind", "deadline_date", "message", "created_at")


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ("notification", "recipient", "channel", "status", "provider", "sent_at")
    list_filter = ("channel", "status", "provider")
    readonly_fields = ("id", "notification", "recipient", "channel", "destination", "status", "provider", "provider_message_id", "error_message", "attempted_at", "sent_at", "created_at")
