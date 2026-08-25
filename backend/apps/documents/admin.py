from django.contrib import admin

from apps.common.services.date_service import format_dual_date
from apps.documents.models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "shipment_part",
        "fob_amount",
        "freight_amount",
        "total_amount",
        "submission_date_dual",
        "created_at",
    )

    search_fields = (
        "shipment_part__reference_number",
        "shipment_part__currency_purchase__registration_order__order_number",
        "shipment_part__currency_purchase__registration_order__company__name",
        "shipment_part__currency_purchase__registration_order__company__national_id",
    )

    readonly_fields = (
        "id",
        "total_amount",
        "submission_date_dual",
        "created_at",
        "updated_at",
    )

    def submission_date_dual(self, obj):
        return format_dual_date(obj.submission_date)

    submission_date_dual.short_description = "Submission Date"
