from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "national_id",
        "company_type",
        "is_active",
        "created_at",
    )

    list_filter = (
        "company_type",
        "is_active",
    )

    search_fields = (
        "name",
        "national_id",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )