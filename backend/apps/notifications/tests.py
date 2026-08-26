from rest_framework import status
from rest_framework.test import APITestCase


from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.companies.models import Company
from apps.notifications.models import NotificationLog
from apps.notifications.services.notification_service import (
    send_notification,
    should_send_notification,
)
from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.services.purchase_service import (
    create_currency_purchase,
)
from apps.notifications.services.message_service import (
    get_notification_message,
)
from apps.trade_orders.services.deadline_service import DeadlineStatus
from apps.notifications.services.deadline_notification_service import (
    process_deadline_notifications,
)
from apps.trade_orders.services.shipment_service import (
    create_shipment_part,
)

class NotificationServiceTests(TestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Notification Test Company",
            national_id="9988776655",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="NOTIF-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        self.purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

    def test_notification_should_be_sent_when_not_sent_before(self):
        result = should_send_notification(
            purchase=self.purchase,
            today=self.purchase.deadline,
        )

        self.assertTrue(result)

    def test_notification_should_not_be_sent_twice(self):
        NotificationLog.objects.create(
            currency_purchase=self.purchase,
            notification_type="LAST_DAY",
        )

        result = should_send_notification(
            purchase=self.purchase,
            today=self.purchase.deadline,
        )

        self.assertFalse(result)

    def test_completed_purchase_should_not_send_notification(self):
        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("40000"),
        )

        result = should_send_notification(
            purchase=self.purchase,
            today=self.purchase.deadline,
        )

        self.assertFalse(result)

    def test_normal_period_should_not_send_notification(self):
        result = should_send_notification(
            purchase=self.purchase,
            today=date(2027, 1, 8),
        )

        self.assertFalse(result)

    def test_different_notification_types_can_be_sent(self):
        NotificationLog.objects.create(
            currency_purchase=self.purchase,
            notification_type="THIRTY_DAYS",
        )

        result = should_send_notification(
            purchase=self.purchase,
            today=self.purchase.deadline,
        )

        self.assertTrue(result)


    def test_send_notification_creates_log(self):
        result = send_notification(
            purchase=self.purchase,
            today=self.purchase.deadline,
        )

        self.assertTrue(result)

        self.assertTrue(
            NotificationLog.objects.filter(
                currency_purchase=self.purchase,
                notification_type="LAST_DAY",
            ).exists()
        )

    def test_send_notification_does_not_create_duplicate_log(self):
        first_result = send_notification(
            purchase=self.purchase,
            today=self.purchase.deadline,
        )

        second_result = send_notification(
            purchase=self.purchase,
            today=self.purchase.deadline,
        )

        self.assertTrue(first_result)
        self.assertFalse(second_result)

        self.assertEqual(
            NotificationLog.objects.filter(
                currency_purchase=self.purchase,
                notification_type="LAST_DAY",
            ).count(),
            1,
        )

    def test_notification_messages_are_defined_for_all_warning_statuses(self):
        statuses = [
            DeadlineStatus.NINETY_DAYS,
            DeadlineStatus.SIXTY_DAYS,
            DeadlineStatus.THIRTY_DAYS,
            DeadlineStatus.TWENTY_DAYS,
            DeadlineStatus.TEN_DAYS,
            DeadlineStatus.FIVE_DAYS,
            DeadlineStatus.LAST_DAY,
            DeadlineStatus.OVERDUE,
        ]

        for status in statuses:
            message = get_notification_message(
                status=status,
                purchase_date=self.purchase.purchase_date,
                deadline=self.purchase.deadline,
                purchase_amount=self.purchase.amount,
                remaining_amount=Decimal("40000"),
                currency=self.purchase.currency,
            )

            self.assertIsNotNone(message)
            self.assertNotEqual(message.strip(), "")

    def test_notification_message_contains_both_calendar_dates(self):
        message = get_notification_message(
            status=DeadlineStatus.THIRTY_DAYS,
            purchase_date=self.purchase.purchase_date,
            deadline=self.purchase.deadline,
            purchase_amount=self.purchase.amount,
            remaining_amount=Decimal("40000"),
            currency=self.purchase.currency,
        )

        self.assertIn(
            "تاریخ خرید: 1405/05/31 (2026/08/22)",
            message,
        )

        self.assertIn(
            "مهلت ارائه اسناد: 1405/12/03 (2027/02/22)",
            message,
        )

    def test_process_deadline_notifications_sends_due_notification(self):
        result = process_deadline_notifications(
            today=self.purchase.deadline,
        )

        self.assertEqual(
            result["processed_count"],
            1,
        )

        self.assertEqual(
            result["sent_count"],
            1,
        )

        self.assertTrue(
            NotificationLog.objects.filter(
                currency_purchase=self.purchase,
                notification_type="LAST_DAY",
            ).exists()
        )

    def test_process_deadline_notifications_does_not_send_duplicate(self):
        first_result = process_deadline_notifications(
            today=self.purchase.deadline,
        )

        second_result = process_deadline_notifications(
            today=self.purchase.deadline,
        )

        self.assertEqual(
            first_result["sent_count"],
            1,
        )

        self.assertEqual(
            second_result["sent_count"],
            0,
        )

        self.assertEqual(
            NotificationLog.objects.filter(
                currency_purchase=self.purchase,
                notification_type="LAST_DAY",
            ).count(),
            1,
        )

    def test_process_deadline_notifications_processes_existing_purchase(self):
        result = process_deadline_notifications(
            today=self.purchase.deadline,
        )

        self.assertEqual(
            result["processed_count"],
            1,
        )

        self.assertEqual(
            result["sent_count"],
            1,
        )

    def test_notification_message_uses_purchase_currency(self):
        message = get_notification_message(
            status=DeadlineStatus.THIRTY_DAYS,
            purchase_date=self.purchase.purchase_date,
            deadline=self.purchase.deadline,
            purchase_amount=Decimal("40000"),
            remaining_amount=Decimal("20000"),
            currency="EUR",
        )

        self.assertIn(
            "مبلغ خرید ارز: 40000 EUR",
            message,
        )

        self.assertIn(
            "مبلغ باقی‌مانده: 20000 EUR",
            message,
        )

class NotificationLogAPITests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Notification API Company",
            national_id="1122334455",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="NOTIF-API-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        self.purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

        self.notification = NotificationLog.objects.create(
            currency_purchase=self.purchase,
            notification_type="THIRTY_DAYS",
        )

        self.list_url = "/api/notifications/logs/"
        self.detail_url = (
            f"/api/notifications/logs/{self.notification.id}/"
        )

    def test_notification_log_list_can_be_read(self):
        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["notification_type"],
            "THIRTY_DAYS",
        )

        self.assertEqual(
            response.data[0]["company_name"],
            "Notification API Company",
        )

        self.assertEqual(
            response.data[0]["order_number"],
            "NOTIF-API-001",
        )

    def test_notification_log_detail_can_be_read(self):
        response = self.client.get(
            self.detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["notification_type"],
            "THIRTY_DAYS",
        )

    def test_notification_log_cannot_be_created_through_api(self):
        response = self.client.post(
            self.list_url,
            {
                "currency_purchase": str(self.purchase.id),
                "notification_type": "SIXTY_DAYS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertEqual(
            NotificationLog.objects.count(),
            1,
        )

    def test_notification_log_cannot_be_deleted_through_api(self):
        response = self.client.delete(
            self.detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertTrue(
            NotificationLog.objects.filter(
                id=self.notification.id,
            ).exists()
        )