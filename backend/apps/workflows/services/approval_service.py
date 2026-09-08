from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.services.purchase_service import (
    create_currency_purchase,
)
from apps.workflows.models import ApprovalRequest
from apps.workflows.services.submission_service import (
    CURRENCY_PURCHASE_TARGET,
)


def _validate_checker(
    *,
    approval_request: ApprovalRequest,
    checker,
) -> None:
    if approval_request.maker_id == checker.pk:
        raise ValidationError(
            "The maker cannot review their own request."
        )

    if not checker.has_perm(
        "workflows.review_approvalrequest"
    ):
        raise ValidationError(
            "You do not have permission to review approval requests."
        )


def _validate_pending(
    *,
    approval_request: ApprovalRequest,
) -> None:
    if (
        approval_request.status
        != ApprovalRequest.Status.PENDING
    ):
        raise ValidationError(
            "This approval request has already been reviewed."
        )


def _parse_uuid(
    value,
    *,
    field_name: str,
) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError, AttributeError):
        raise ValidationError(
            f"Invalid {field_name}."
        )


def _parse_decimal(
    value,
    *,
    field_name: str,
) -> Decimal:
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(
            f"Invalid {field_name}."
        )

    if not decimal_value.is_finite():
        raise ValidationError(
            f"Invalid {field_name}."
        )

    return decimal_value


def _parse_date(
    value,
    *,
    field_name: str,
) -> date:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ValidationError(
            f"Invalid {field_name}."
        )


def _apply_currency_purchase_create(
    *,
    approval_request: ApprovalRequest,
):
    if (
        approval_request.operation
        != ApprovalRequest.Operation.CREATE
    ):
        raise ValidationError(
            "Invalid operation for currency purchase workflow."
        )

    payload = approval_request.payload

    if not isinstance(payload, dict):
        raise ValidationError(
            "Invalid approval request payload."
        )

    required_fields = {
        "registration_order_id",
        "amount",
        "currency",
        "purchase_date",
    }

    if set(payload.keys()) != required_fields:
        raise ValidationError(
            "Invalid approval request payload."
        )

    registration_order_id = _parse_uuid(
        payload["registration_order_id"],
        field_name="registration order ID",
    )

    amount = _parse_decimal(
        payload["amount"],
        field_name="purchase amount",
    )

    currency = str(
        payload["currency"]
    ).strip().upper()

    if not currency:
        raise ValidationError(
            "Invalid purchase currency."
        )

    purchase_date = _parse_date(
        payload["purchase_date"],
        field_name="purchase date",
    )

    try:
        registration_order = (
            RegistrationOrder.objects.get(
                pk=registration_order_id
            )
        )
    except RegistrationOrder.DoesNotExist:
        raise ValidationError(
            "Registration order does not exist."
        )

    return create_currency_purchase(
        registration_order=registration_order,
        amount=amount,
        currency=currency,
        purchase_date=purchase_date,
    )


def _apply_request(
    *,
    approval_request: ApprovalRequest,
):
    if (
        approval_request.target_type
        == CURRENCY_PURCHASE_TARGET
    ):
        return _apply_currency_purchase_create(
            approval_request=approval_request,
        )

    raise ValidationError(
        "Unsupported approval request target type."
    )


@transaction.atomic
def approve_request(
    *,
    approval_request: ApprovalRequest,
    checker,
) -> ApprovalRequest:

    locked_request = (
        ApprovalRequest.objects
        .select_for_update()
        .get(pk=approval_request.pk)
    )

    _validate_pending(
        approval_request=locked_request,
    )

    _validate_checker(
        approval_request=locked_request,
        checker=checker,
    )

    created_object = _apply_request(
        approval_request=locked_request,
    )

    locked_request.target_id = created_object.pk
    locked_request.status = (
        ApprovalRequest.Status.APPROVED
    )
    locked_request.checker = checker
    locked_request.reviewed_at = timezone.now()

    locked_request.save(
        update_fields=(
            "target_id",
            "status",
            "checker",
            "reviewed_at",
        )
    )

    return locked_request


@transaction.atomic
def reject_request(
    *,
    approval_request: ApprovalRequest,
    checker,
    reason: str,
) -> ApprovalRequest:

    locked_request = (
        ApprovalRequest.objects
        .select_for_update()
        .get(pk=approval_request.pk)
    )

    _validate_pending(
        approval_request=locked_request,
    )

    _validate_checker(
        approval_request=locked_request,
        checker=checker,
    )

    reason = reason.strip()

    if not reason:
        raise ValidationError(
            "A rejection reason is required."
        )

    locked_request.status = (
        ApprovalRequest.Status.REJECTED
    )
    locked_request.checker = checker
    locked_request.review_comment = reason
    locked_request.reviewed_at = timezone.now()

    locked_request.save(
        update_fields=(
            "status",
            "checker",
            "review_comment",
            "reviewed_at",
        )
    )

    return locked_request