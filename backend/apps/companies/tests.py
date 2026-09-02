from rest_framework import status
from rest_framework.test import APITestCase

from apps.companies.models import Company
from rest_framework.test import APIClient
from apps.trade_orders.models import RegistrationOrder

from decimal import Decimal
from django.contrib.auth import get_user_model

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class CompanyAPITests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="company-test-user",
            password="StrongTestPassword123!",
        )

        company_content_type = ContentType.objects.get_for_model(
            Company,
        )

        company_permissions = Permission.objects.filter(
            content_type=company_content_type,
            codename__in=[
                "view_company",
                "add_company",
                "change_company",
                "delete_company",
            ],
        )

        self.user.user_permissions.add(
            *company_permissions,
        )

        self.client.force_authenticate(
            user=self.user,
        )

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

    def test_delete_company_without_orders(self):
        company = Company.objects.create(
            name="Delete Allowed",
            national_id="9000000001",
            company_type="COMMERCIAL",
        )

        response = self.client.delete(
            f"/api/companies/{company.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Company.objects.filter(id=company.id).exists()
        )

    def test_delete_company_with_registration_order_is_protected(self):
        company = Company.objects.create(
            name="Protected Company",
            national_id="9000000002",
            company_type="COMMERCIAL",
        )

        RegistrationOrder.objects.create(
            company=company,
            order_number="PROTECT-001",
            registered_amount=Decimal("10000"),
            currency="USD",
        )

        response = self.client.delete(
            f"/api/companies/{company.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        self.assertEqual(
            response.data["detail"],
            (
                "This company cannot be deleted because "
                "it has related registration orders."
            ),
        )

        self.assertTrue(
            Company.objects.filter(id=company.id).exists()
        )

    def test_authenticated_user_without_permissions_cannot_view_companies(self):
        user = get_user_model().objects.create_user(
            username="company-no-permission-user",
            password="StrongTestPass123!",
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_with_view_permission_can_view_companies(self):
        user = get_user_model().objects.create_user(
            username="company-viewer-user",
            password="StrongTestPass123!",
        )

        content_type = ContentType.objects.get_for_model(
            Company,
        )

        view_permission = Permission.objects.get(
            content_type=content_type,
            codename="view_company",
        )

        user.user_permissions.add(view_permission)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
