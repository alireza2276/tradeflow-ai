from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.trade_orders.models import (
    CurrencyPurchase,
    RegistrationOrder,
)
from apps.trade_orders.services.purchase_service import (
    create_currency_purchase,
    update_currency_purchase,
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
    if not isinstance(value, str):
        raise ValidationError(
            f"Invalid {field_name}."
        )

    try:
        return UUID(value)
    except (TypeError, ValueError, AttributeError):
        raise ValidationError(
            f"Invalid {field_name}."
        )


def _parse_decimal(
    value,
    *,
    field_name: str,
) -> Decimal:
    if not isinstance(value, str):
        raise ValidationError(
            f"Invalid {field_name}."
        )

    try:
        decimal_value = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(
            f"Invalid {field_name}."
        )

    if not decimal_value.is_finite():
        raise ValidationError(
            f"Invalid {field_name}."
        )

    if decimal_value <= 0:
        raise ValidationError(
            f"{field_name} must be greater than zero."
        )

    return decimal_value


def _parse_date(
    value,
    *,
    field_name: str,
) -> date:
    if not isinstance(value, str):
        raise ValidationError(
            f"Invalid {field_name}."
        )

    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError(
            f"Invalid {field_name}."
        )


def _parse_version(
    value,
) -> datetime:
    if not isinstance(value, str):
        raise ValidationError(
            "Invalid approval request version."
        )

    parsed_version = parse_datetime(value)

    if parsed_version is None:
        raise ValidationError(
            "Invalid approval request version."
        )

    if timezone.is_naive(parsed_version):
        raise ValidationError(
            "Invalid approval request version."
        )

    return parsed_version


def _validate_exact_keys(
    payload,
    *,
    expected_keys: set[str],
    field_name: str,
) -> None:
    if not isinstance(payload, dict):
        raise ValidationError(
            f"Invalid {field_name}."
        )

    if set(payload.keys()) != expected_keys:
        raise ValidationError(
            f"Invalid {field_name}."
        )


def _apply_currency_purchase_create(
    *,
    approval_request: ApprovalRequest,
) -> CurrencyPurchase:
    if approval_request.target_id is not None:
        raise ValidationError(
            "Create approval request must not already "
            "reference a target object."
        )

    payload = approval_request.payload

    _validate_exact_keys(
        payload,
        expected_keys={
            "registration_order_id",
            "amount",
            "currency",
            "purchase_date",
        },
        field_name="approval request payload",
    )

    registration_order_id = _parse_uuid(
        payload["registration_order_id"],
        field_name="registration order ID",
    )

    amount = _parse_decimal(
        payload["amount"],
        field_name="purchase amount",
    )

    currency = payload["currency"]

    if not isinstance(currency, str):
        raise ValidationError(
            "Invalid purchase currency."
        )

    if (
        not currency
        or currency != currency.strip()
        or currency != currency.upper()
    ):
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


def _apply_currency_purchase_correction(
    *,
    approval_request: ApprovalRequest,
) -> CurrencyPurchase:
    if approval_request.target_id is None:
        raise ValidationError(
            "Correction approval request must reference "
            "an existing currency purchase."
        )

    payload = approval_request.payload

    _validate_exact_keys(
        payload,
        expected_keys={
            "version",
            "before",
            "proposed",
        },
        field_name="approval request payload",
    )

    before = payload["before"]
    proposed = payload["proposed"]

    _validate_exact_keys(
        before,
        expected_keys={
            "amount",
            "currency",
            "purchase_date",
        },
        field_name="before snapshot",
    )

    _validate_exact_keys(
        proposed,
        expected_keys={
            "amount",
            "currency",
            "purchase_date",
        },
        field_name="proposed correction",
    )

    expected_version = _parse_version(
        payload["version"]
    )

    before_amount = _parse_decimal(
        before["amount"],
        field_name="before purchase amount",
    )

    before_currency = before["currency"]

    if not isinstance(before_currency, str):
        raise ValidationError(
            "Invalid before purchase currency."
        )

    before_purchase_date = _parse_date(
        before["purchase_date"],
        field_name="before purchase date",
    )

    proposed_amount = _parse_decimal(
        proposed["amount"],
        field_name="proposed purchase amount",
    )

    proposed_currency = proposed["currency"]

    if not isinstance(proposed_currency, str):
        raise ValidationError(
            "Invalid proposed purchase currency."
        )

    proposed_purchase_date = _parse_date(
        proposed["purchase_date"],
        field_name="proposed purchase date",
    )

    try:
        purchase_reference = (
            CurrencyPurchase.objects
            .only("registration_order_id")
            .get(pk=approval_request.target_id)
        )
    except CurrencyPurchase.DoesNotExist:
        raise ValidationError(
            "Currency purchase does not exist."
        )

    locked_order = (
        RegistrationOrder.objects
        .select_for_update()
        .get(
            pk=purchase_reference.registration_order_id
        )
    )

    try:
        locked_purchase = (
            CurrencyPurchase.objects
            .select_for_update()
            .get(pk=approval_request.target_id)
        )
    except CurrencyPurchase.DoesNotExist:
        raise ValidationError(
            "Currency purchase does not exist."
        )

    if (
        locked_purchase.registration_order_id
        != locked_order.pk
    ):
        raise ValidationError(
            "Currency purchase registration order changed "
            "during the correction operation."
        )

    if locked_purchase.updated_at != expected_version:
        raise ValidationError(
            "The currency purchase has changed since "
            "this correction request was submitted."
        )

    if (
        locked_purchase.amount != before_amount
        or locked_purchase.currency != before_currency
        or locked_purchase.purchase_date
        != before_purchase_date
    ):
        raise ValidationError(
            "The currency purchase no longer matches "
            "the original correction snapshot."
        )

    if proposed_currency != locked_order.currency:
        raise ValidationError(
            "Proposed currency must match "
            "the registration order currency."
        )

    if proposed_currency != before_currency:
        raise ValidationError(
            "Currency cannot be changed through "
            "a currency purchase correction."
        )

    return update_currency_purchase(
        purchase=locked_purchase,
        amount=proposed_amount,
        purchase_date=proposed_purchase_date,
    )

def _apply_currency_purchase_void(
    *,
    approval_request: ApprovalRequest,
    checker,
) -> CurrencyPurchase:
    if approval_request.target_id is None:
        raise ValidationError(
            "Void approval request must reference "
            "an existing currency purchase."
        )

    payload = approval_request.payload

    _validate_exact_keys(
        payload,
        expected_keys={
            "version",
            "before",
        },
        field_name="approval request payload",
    )

    before = payload["before"]

    _validate_exact_keys(
        before,
        expected_keys={
            "amount",
            "currency",
            "purchase_date",
            "registration_order_id",
        },
        field_name="before snapshot",
    )

    expected_version = _parse_version(
        payload["version"]
    )

    before_amount = _parse_decimal(
        before["amount"],
        field_name="before purchase amount",
    )

    before_currency = before["currency"]

    if not isinstance(before_currency, str):
        raise ValidationError(
            "Invalid before purchase currency."
        )

    before_purchase_date = _parse_date(
        before["purchase_date"],
        field_name="before purchase date",
    )

    before_order_id = _parse_uuid(
        before["registration_order_id"],
        field_name="before registration order ID",
    )

    try:
        purchase_reference = (
            CurrencyPurchase.objects
            .only("registration_order_id")
            .get(pk=approval_request.target_id)
        )
    except CurrencyPurchase.DoesNotExist:
        raise ValidationError(
            "Currency purchase does not exist."
        )

    locked_order = (
        RegistrationOrder.objects
        .select_for_update()
        .get(
            pk=purchase_reference.registration_order_id
        )
    )

    try:
        locked_purchase = (
            CurrencyPurchase.objects
            .select_for_update()
            .get(pk=approval_request.target_id)
        )
    except CurrencyPurchase.DoesNotExist:
        raise ValidationError(
            "Currency purchase does not exist."
        )

    if (
        locked_purchase.registration_order_id
        != locked_order.pk
    ):
        raise ValidationError(
            "Currency purchase registration order changed "
            "during the void operation."
        )

    if locked_purchase.is_void:
        raise ValidationError(
            "Currency purchase is already void."
        )

    if locked_purchase.updated_at != expected_version:
        raise ValidationError(
            "The currency purchase has changed since "
            "this void request was submitted."
        )

    if (
        locked_purchase.registration_order_id
        != before_order_id
        or locked_purchase.amount != before_amount
        or locked_purchase.currency != before_currency
        or locked_purchase.purchase_date
        != before_purchase_date
    ):
        raise ValidationError(
            "The currency purchase no longer matches "
            "the original void snapshot."
        )

    if locked_purchase.shipment_parts.exists():
        raise ValidationError(
            "Currency purchase with shipment parts "
            "cannot be voided."
        )

    void_reason = approval_request.reason.strip()

    if not void_reason:
        raise ValidationError(
            "A void reason is required."
        )

    locked_purchase.is_void = True
    locked_purchase.voided_at = timezone.now()
    locked_purchase.voided_by = checker
    locked_purchase.void_reason = void_reason

    locked_purchase.save(
        update_fields=(
            "is_void",
            "voided_at",
            "voided_by",
            "void_reason",
            "updated_at",
        )
    )

    return locked_purchase


def _apply_request(
    *,
    approval_request: ApprovalRequest,
    checker,
):
    if (
        approval_request.target_type
        != CURRENCY_PURCHASE_TARGET
    ):
        raise ValidationError(
            "Unsupported approval request target type."
        )

    if (
        approval_request.operation
        == ApprovalRequest.Operation.CREATE
    ):
        return _apply_currency_purchase_create(
            approval_request=approval_request,
        )

    if (
        approval_request.operation
        == ApprovalRequest.Operation.CORRECT
    ):
        return _apply_currency_purchase_correction(
            approval_request=approval_request,
        )

    if (
            approval_request.operation
            == ApprovalRequest.Operation.VOID
    ):
        return _apply_currency_purchase_void(
            approval_request=approval_request,
            checker=checker,
        )

    raise ValidationError(
        "Unsupported approval request operation."
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

    applied_object = _apply_request(
        approval_request=locked_request,
        checker=checker,
    )

    locked_request.target_id = applied_object.pk
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