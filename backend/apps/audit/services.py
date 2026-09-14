from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.db import models

from apps.audit.context import (
    get_current_actor,
    get_current_request_metadata,
)
from apps.audit.models import AuditEvent


def _json_safe(value):
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Decimal):
        return format(value, "f")

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]

    return str(value)


def snapshot_instance(instance) -> dict:
    if instance is None:
        return {}

    snapshot = {}

    for field in instance._meta.concrete_fields:
        value = getattr(instance, field.attname)
        snapshot[field.name] = _json_safe(value)

    return snapshot


def get_target_type(instance) -> str:
    return (
        f"{instance._meta.app_label}."
        f"{instance._meta.model_name}"
    )


def log_audit_event(
    *,
    action: str,
    target_type: str,
    target_id="",
    actor=None,
    approval_request=None,
    before_state=None,
    after_state=None,
    reason="",
    metadata=None,
) -> AuditEvent:
    resolved_actor = (
        actor
        if actor is not None
        else get_current_actor()
    )

    request_metadata = get_current_request_metadata()
    merged_metadata = {
        **request_metadata,
        **(metadata or {}),
    }

    return AuditEvent.objects.create(
        action=action,
        actor=resolved_actor,
        target_type=target_type,
        target_id=str(target_id or ""),
        approval_request=approval_request,
        before_state=_json_safe(before_state or {}),
        after_state=_json_safe(after_state or {}),
        reason=(reason or "").strip(),
        metadata=_json_safe(merged_metadata),
    )
