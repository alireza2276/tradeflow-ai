from rest_framework import status
from rest_framework.test import APITestCase

from apps.companies.models import Company


class CompanyAPITests(APITestCase):

    def setUp(self):
        self.url = "/api/companies/"

        self.company = Company.objects.create(
            name="Existing Company",
            national_id="1234567890",
            company_type="COMMERCIAL",
            phone="09120000000",
            email="existing@example.com",
            is_active=True,
        )

    def test_company_list_returns_success(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_company_can_be_created(self):
        payload = {
            "name": "New Company",
            "national_id": "9876543210",
            "company_type": "PRODUCTION",
            "phone": "09121111111",
            "email": "new@example.com",
            "is_active": True,
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Company.objects.filter(
                national_id="9876543210",
            ).exists()
        )

    def test_duplicate_national_id_is_rejected(self):
        payload = {
            "name": "Duplicate Company",
            "national_id": "1234567890",
            "company_type": "COMMERCIAL",
            "phone": "09122222222",
            "email": "duplicate@example.com",
            "is_active": True,
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_company_type_is_rejected(self):
        payload = {
            "name": "Invalid Company",
            "national_id": "5555555555",
            "company_type": "UNKNOWN",
            "phone": "09123333333",
            "email": "invalid@example.com",
            "is_active": True,
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
