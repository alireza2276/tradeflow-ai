from django.db.models.signals import (
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)
from django.dispatch import receiver

from apps.audit.models import AuditEvent
from apps.audit.services import (
    get_target_type,
    log_audit_event,
    snapshot_instance,
)
from apps.companies.models import Company
from apps.documents.models import Invoice
from apps.trade_orders.models import (
    CurrencyPurchase,
    PaymentInstrument,
    RegistrationOrder,
    ShipmentPart,
    RegulatoryRule,
    DeadlineExtension,
    CustomsClearance,
    RegulatoryDeadline,
)
from apps.workflows.models import ApprovalRequest


TRACKED_MODELS = (
    Company,
    RegistrationOrder,
    PaymentInstrument,
    CurrencyPurchase,
    ShipmentPart,
    Invoice,
    RegulatoryRule,
    DeadlineExtension,
    CustomsClearance,
    RegulatoryDeadline,
)


def _load_previous(instance):
    if not instance.pk:
        return None

    try:
        return instance.__class__.objects.get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return None


@receiver(pre_save)
def capture_before_state(sender, instance, **kwargs):
    if sender not in TRACKED_MODELS:
        return

    previous = _load_previous(instance)
    instance._audit_before_state = (
        snapshot_instance(previous)
        if previous is not None
        else {}
    )


@receiver(post_save)
def audit_tracked_model_save(sender, instance, created, **kwargs):
    if sender not in TRACKED_MODELS:
        return

    before_state = getattr(
        instance,
        "_audit_before_state",
        {},
    )
    after_state = snapshot_instance(instance)

    action = AuditEvent.Action.CREATE if created else AuditEvent.Action.UPDATE

    if (
        sender in (CurrencyPurchase, ShipmentPart)
        and not created
        and not before_state.get("is_void")
        and after_state.get("is_void")
    ):
        action = AuditEvent.Action.VOID

    log_audit_event(
        action=action,
        target_type=get_target_type(instance),
        target_id=instance.pk,
        before_state=before_state,
        after_state=after_state,
    )


@receiver(pre_delete)
def capture_delete_state(sender, instance, **kwargs):
    if sender not in TRACKED_MODELS:
        return

    instance._audit_delete_state = snapshot_instance(instance)


@receiver(post_delete)
def audit_tracked_model_delete(sender, instance, **kwargs):
    if sender not in TRACKED_MODELS:
        return

    log_audit_event(
        action=AuditEvent.Action.DELETE,
        target_type=get_target_type(instance),
        target_id=instance.pk,
        before_state=getattr(
            instance,
            "_audit_delete_state",
            {},
        ),
        after_state={},
    )


@receiver(pre_save, sender=ApprovalRequest)
def capture_approval_before_state(sender, instance, **kwargs):
    previous = _load_previous(instance)
    instance._audit_previous_approval = previous


@receiver(post_save, sender=ApprovalRequest)
def audit_approval_request(sender, instance, created, **kwargs):
    if created:
        payload = instance.payload or {}
        before_state = payload.get("before", {})
        after_state = (
            payload.get("proposed")
            or payload
        )

        log_audit_event(
            action=AuditEvent.Action.REQUEST_SUBMITTED,
            actor=instance.maker,
            target_type=instance.target_type,
            target_id=instance.target_id or "",
            approval_request=instance,
            before_state=before_state,
            after_state=after_state,
            reason=instance.reason,
            metadata={
                "operation": instance.operation,
            },
        )
        return

    previous = getattr(
        instance,
        "_audit_previous_approval",
        None,
    )

    if previous is None:
        return

    if previous.status == instance.status:
        return

    if instance.status == ApprovalRequest.Status.APPROVED:
        action = AuditEvent.Action.REQUEST_APPROVED
        reason = instance.reason
    elif instance.status == ApprovalRequest.Status.REJECTED:
        action = AuditEvent.Action.REQUEST_REJECTED
        reason = instance.review_comment
    else:
        return

    payload = instance.payload or {}

    log_audit_event(
        action=action,
        actor=instance.checker,
        target_type=instance.target_type,
        target_id=instance.target_id or "",
        approval_request=instance,
        before_state=payload.get("before", {}),
        after_state=(
            payload.get("proposed")
            or payload
        ),
        reason=reason,
        metadata={
            "operation": instance.operation,
            "maker_id": str(instance.maker_id),
        },
    )
