from datetime import date

from django.test import SimpleTestCase

from apps.common.services.date_service import (
    format_dual_date,
    gregorian_to_jalali,
)


class DateServiceTests(SimpleTestCase):

    def test_gregorian_to_jalali(self):
        result = gregorian_to_jalali(
            date(2026, 8, 23)
        )

        self.assertEqual(
            result,
            "1405/06/01",
        )

    def test_format_dual_date(self):
        result = format_dual_date(
            date(2026, 8, 23)
        )

        self.assertEqual(
            result,
            "1405/06/01 (2026/08/23)",
        )