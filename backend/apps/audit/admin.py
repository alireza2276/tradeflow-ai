from django.contrib import admin

from apps.audit.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "actor",
        "target_type",
        "target_id",
    )
    list_filter = (
        "action",
        "target_type",
        "created_at",
    )
    search_fields = (
        "actor__username",
        "target_type",
        "target_id",
        "reason",
    )
    readonly_fields = (
        "id",
        "action",
        "actor",
        "target_type",
        "target_id",
        "approval_request",
        "before_state",
        "after_state",
        "reason",
        "metadata",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
