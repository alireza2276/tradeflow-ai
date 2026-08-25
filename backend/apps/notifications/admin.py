from django.contrib import admin

from apps.notifications.models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "currency_purchase",
        "company_name",
        "registration_order_number",
        "notification_type",
        "sent_at",
    )

    search_fields = (
        "currency_purchase__registration_order__company__name",
        "currency_purchase__registration_order__company__national_id",
        "currency_purchase__registration_order__order_number",
        "notification_type",
    )

    list_filter = (
        "notification_type",
        "sent_at",
    )

    readonly_fields = (
        "id",
        "currency_purchase",
        "notification_type",
        "sent_at",
    )

    ordering = (
        "-sent_at",
    )

    def company_name(self, obj):
        return obj.currency_purchase.registration_order.company.name

    company_name.short_description = "Company"

    def registration_order_number(self, obj):
        return obj.currency_purchase.registration_order.order_number

    registration_order_number.short_description = "Registration Order"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False