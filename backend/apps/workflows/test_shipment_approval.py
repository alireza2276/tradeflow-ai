from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase

from apps.companies.models import Company
from apps.trade_orders.models import RegistrationOrder, ShipmentPart
from apps.common.test_regulatory_helpers import create_test_currency_purchase as create_currency_purchase
from apps.workflows.models import ApprovalRequest
from apps.workflows.services.approval_service import approve_request
from apps.workflows.services.submission_service import (
    submit_shipment_part_correction,
    submit_shipment_part_create,
    submit_shipment_part_void,
)


class ShipmentPartApprovalWorkflowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.maker = user_model.objects.create_user(
            username="shipment-maker",
            password="StrongTestPass123!",
        )
        self.checker = user_model.objects.create_user(
            username="shipment-checker",
            password="StrongTestPass123!",
        )

        self.maker.user_permissions.add(
            Permission.objects.get(codename="add_shipmentpart"),
            Permission.objects.get(codename="change_shipmentpart"),
            Permission.objects.get(codename="void_shipmentpart"),
        )
        self.checker.user_permissions.add(
            Permission.objects.get(codename="review_approvalrequest"),
        )

        company = Company.objects.create(
            name="Shipment Approval Company",
            national_id="9988776655",
            company_type="COMMERCIAL",
        )
        order = RegistrationOrder.objects.create(
            company=company,
            order_number="SHIP-APPROVAL-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )
        self.purchase = create_currency_purchase(
            registration_order=order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
        )

    def test_create_correct_and_void_shipment_through_maker_checker(self):
        create_request = submit_shipment_part_create(
            maker=self.maker,
            currency_purchase=self.purchase,
            amount=Decimal("20000"),
            shipment_date=date(2026, 9, 2),
            received_date=date(2026, 9, 5),
            reference_number="SHIP-001",
            notes="Initial shipment",
        )
        self.assertEqual(create_request.status, ApprovalRequest.Status.PENDING)
        self.assertEqual(ShipmentPart.objects.count(), 0)

        approved_create = approve_request(
            approval_request=create_request,
            checker=self.checker,
        )
        shipment = ShipmentPart.objects.get(pk=approved_create.target_id)
        self.assertEqual(shipment.amount, Decimal("20000"))

        correction_request = submit_shipment_part_correction(
            maker=self.maker,
            shipment=shipment,
            amount=Decimal("19000"),
            shipment_date=shipment.shipment_date,
            received_date=shipment.received_date,
            reference_number="SHIP-001-REV",
            notes="Corrected shipment",
            reason="Correct reference and amount",
        )
        approve_request(
            approval_request=correction_request,
            checker=self.checker,
        )
        shipment.refresh_from_db()
        self.assertEqual(shipment.amount, Decimal("19000"))
        self.assertEqual(shipment.reference_number, "SHIP-001-REV")

        void_request = submit_shipment_part_void(
            maker=self.maker,
            shipment=shipment,
            reason="Shipment document cancelled",
        )
        approve_request(
            approval_request=void_request,
            checker=self.checker,
        )
        shipment.refresh_from_db()
        self.assertTrue(shipment.is_void)
        self.assertEqual(shipment.voided_by, self.checker)
        self.assertEqual(shipment.void_reason, "Shipment document cancelled")
