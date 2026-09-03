from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import Client, TestCase
from rest_framework.test import APIClient
import json

class AuthenticationTests(TestCase):

    def setUp(self):
        self.client = Client(
            enforce_csrf_checks=True,
        )

        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="StrongTestPassword123!",
        )

        self.csrf_url = "/api/auth/csrf/"
        self.login_url = "/api/auth/login/"

    def get_csrf_token(self):
        response = self.client.get(
            self.csrf_url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        return self.client.cookies[
            "csrftoken"
        ].value

    def test_login_without_csrf_is_rejected(self):
        response = self.client.post(
            self.login_url,
            data={
                "username": "testuser",
                "password": "StrongTestPassword123!",
            },
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_login_with_invalid_credentials_is_rejected(self):
        csrf_token = self.get_csrf_token()

        response = self.client.post(
            self.login_url,
            data={
                "username": "testuser",
                "password": "WrongPassword123!",
            },
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_login_with_valid_credentials_creates_session(self):
        csrf_token = self.get_csrf_token()

        response = self.client.post(
            self.login_url,
            data={
                "username": "testuser",
                "password": "StrongTestPassword123!",
            },
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "_auth_user_id",
            self.client.session,
        )

        self.assertEqual(
            response.json()["user"]["username"],
            "testuser",
        )

    def test_me_requires_authentication(self):
        response = self.client.get(
            "/api/auth/me/",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_me_returns_authenticated_user(self):
        csrf_token = self.get_csrf_token()

        login_response = self.client.post(
            self.login_url,
            data={
                "username": "testuser",
                "password": "StrongTestPassword123!",
            },
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            login_response.status_code,
            200,
        )

        response = self.client.get(
            "/api/auth/me/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["user"]["username"],
            "testuser",
        )

        self.assertEqual(
            response.json()["user"]["id"],
            self.user.pk,
        )

    def test_logout_without_csrf_is_rejected(self):
        csrf_token = self.get_csrf_token()

        login_response = self.client.post(
            self.login_url,
            data={
                "username": "testuser",
                "password": "StrongTestPassword123!",
            },
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            login_response.status_code,
            200,
        )

        response = self.client.post(
            "/api/auth/logout/",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_logout_ends_session(self):
        csrf_token = self.get_csrf_token()

        login_response = self.client.post(
            self.login_url,
            data={
                "username": "testuser",
                "password": "StrongTestPassword123!",
            },
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            login_response.status_code,
            200,
        )

        csrf_token = self.client.cookies[
            "csrftoken"
        ].value

        response = self.client.post(
            "/api/auth/logout/",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

        me_response = self.client.get(
            "/api/auth/me/",
        )

        self.assertEqual(
            me_response.status_code,
            401,
        )

    def test_financial_api_requires_authentication(self):
        response = self.client.get(
            "/api/trade/registration-orders/"
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_me_returns_user_roles_and_permissions(self):
        user = get_user_model().objects.create_user(
            username="rbac-me-user",
            password="StrongTestPass123!",
        )

        call_command(
            "setup_rbac",
            verbosity=0,
        )

        role = Group.objects.get(
            name="TRADE_VIEWER",
        )

        user.groups.add(role)

        self.client.force_login(user)

        response = self.client.get(
            "/api/auth/me/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertIn(
            "TRADE_VIEWER",
            data["user"]["roles"],
        )

        self.assertIn(
            "trade_orders.view_registrationorder",
            data["user"]["permissions"],
        )

        self.assertIn(
            "trade_orders.view_currencypurchase",
            data["user"]["permissions"],
        )

        self.assertNotIn(
            "trade_orders.add_registrationorder",
            data["user"]["permissions"],
        )

    def test_login_returns_user_roles_and_permissions(self):
        user = get_user_model().objects.create_user(
            username="rbac-login-user",
            password="StrongTestPass123!",
        )

        call_command(
            "setup_rbac",
            verbosity=0,
        )

        role = Group.objects.get(
            name="TRADE_OPERATOR",
        )

        user.groups.add(role)

        csrf_response = self.client.get(
            "/api/auth/csrf/",
        )

        csrf_token = csrf_response.cookies["csrftoken"].value

        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "username": "rbac-login-user",
                    "password": "StrongTestPass123!",
                }
            ),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertIn(
            "TRADE_OPERATOR",
            data["user"]["roles"],
        )

        self.assertIn(
            "trade_orders.add_currencypurchase",
            data["user"]["permissions"],
        )

        self.assertNotIn(
            "trade_orders.add_registrationorder",
            data["user"]["permissions"],
        )

class RBACSetupTests(TestCase):

    def test_setup_rbac_creates_expected_roles(self):
        call_command(
            "setup_rbac",
            verbosity=0,
        )

        expected_roles = {
            "TRADE_VIEWER",
            "TRADE_OPERATOR",
            "TRADE_SUPERVISOR",
            "SECURITY_ADMIN",
        }

        actual_roles = set(
            Group.objects.filter(
                name__in=expected_roles,
            ).values_list(
                "name",
                flat=True,
            )
        )

        self.assertEqual(
            actual_roles,
            expected_roles,
        )

    def test_setup_rbac_is_idempotent(self):
        call_command(
            "setup_rbac",
            verbosity=0,
        )

        call_command(
            "setup_rbac",
            verbosity=0,
        )

        expected_roles = {
            "TRADE_VIEWER",
            "TRADE_OPERATOR",
            "TRADE_SUPERVISOR",
            "SECURITY_ADMIN",
        }

        for role_name in expected_roles:
            self.assertEqual(
                Group.objects.filter(
                    name=role_name,
                ).count(),
                1,
            )

    def test_setup_rbac_assigns_exact_permissions_to_roles(self):
        call_command(
            "setup_rbac",
            verbosity=0,
        )

        expected_permissions = {
            "TRADE_VIEWER": {
                "companies.view_company",
                "documents.view_invoice",
                "notifications.view_notificationlog",
                "trade_orders.view_currencypurchase",
                "trade_orders.view_paymentinstrument",
                "trade_orders.view_registrationorder",
                "trade_orders.view_shipmentpart",
            },
            "TRADE_OPERATOR": {
                "companies.view_company",
                "documents.view_invoice",
                "documents.add_invoice",
                "documents.change_invoice",
                "notifications.view_notificationlog",
                "trade_orders.view_registrationorder",
                "trade_orders.view_paymentinstrument",
                "trade_orders.add_paymentinstrument",
                "trade_orders.change_paymentinstrument",
                "trade_orders.view_currencypurchase",
                "trade_orders.add_currencypurchase",
                "trade_orders.change_currencypurchase",
                "trade_orders.view_shipmentpart",
                "trade_orders.add_shipmentpart",
                "trade_orders.change_shipmentpart",
            },
            "TRADE_SUPERVISOR": {
                "companies.view_company",
                "companies.add_company",
                "companies.change_company",
                "documents.view_invoice",
                "documents.add_invoice",
                "documents.change_invoice",
                "notifications.view_notificationlog",
                "trade_orders.view_registrationorder",
                "trade_orders.add_registrationorder",
                "trade_orders.change_registrationorder",
                "trade_orders.view_paymentinstrument",
                "trade_orders.add_paymentinstrument",
                "trade_orders.change_paymentinstrument",
                "trade_orders.view_currencypurchase",
                "trade_orders.add_currencypurchase",
                "trade_orders.change_currencypurchase",
                "trade_orders.view_shipmentpart",
                "trade_orders.add_shipmentpart",
                "trade_orders.change_shipmentpart",
            },
            "SECURITY_ADMIN": set(),
        }

        for role_name, expected in expected_permissions.items():
            group = Group.objects.get(
                name=role_name,
            )

            actual = {
                (
                    f"{permission.content_type.app_label}."
                    f"{permission.codename}"
                )
                for permission in group.permissions.select_related(
                    "content_type"
                )
            }

            self.assertEqual(
                actual,
                expected,
                f"Unexpected permissions for role {role_name}.",
            )

class RBACAPITests(TestCase):

    def setUp(self):
        call_command(
            "setup_rbac",
            verbosity=0,
        )

        self.client = APIClient()

    def create_user_with_role(self, username, role_name):
        user = get_user_model().objects.create_user(
            username=username,
            password="StrongTestPassword123!",
        )

        role = Group.objects.get(
            name=role_name,
        )

        user.groups.add(
            role,
        )

        return user

    def test_trade_viewer_can_view_registration_orders_but_cannot_create(self):
        user = self.create_user_with_role(
            "trade-viewer-user",
            "TRADE_VIEWER",
        )

        self.client.force_authenticate(
            user=user,
        )

        get_response = self.client.get(
            "/api/trade/registration-orders/",
        )

        post_response = self.client.post(
            "/api/trade/registration-orders/",
            {},
            format="json",
        )

        self.assertEqual(
            get_response.status_code,
            200,
        )

        self.assertEqual(
            post_response.status_code,
            403,
        )

    def test_trade_operator_cannot_create_registration_order(self):
        user = self.create_user_with_role(
            "trade-operator-user",
            "TRADE_OPERATOR",
        )

        self.client.force_authenticate(
            user=user,
        )

        response = self.client.post(
            "/api/trade/registration-orders/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_trade_operator_can_create_currency_purchase(self):
        from decimal import Decimal
        from datetime import date

        from apps.companies.models import Company
        from apps.trade_orders.models import RegistrationOrder

        company = Company.objects.create(
            name="RBAC Operator Company",
            national_id="1122334455",
            company_type="COMMERCIAL",
        )

        order = RegistrationOrder.objects.create(
            company=company,
            order_number="RBAC-OP-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        user = self.create_user_with_role(
            "trade-operator-purchase-user",
            "TRADE_OPERATOR",
        )

        self.client.force_authenticate(
            user=user,
        )

        response = self.client.post(
            "/api/trade/currency-purchases/",
            {
                "registration_order": str(order.pk),
                "amount": "50000",
                "currency": "USD",
                "purchase_date": date.today().isoformat(),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_trade_supervisor_can_create_company(self):
        user = self.create_user_with_role(
            "trade-supervisor-user",
            "TRADE_SUPERVISOR",
        )

        self.client.force_authenticate(
            user=user,
        )

        response = self.client.post(
            "/api/companies/",
            {
                "name": "RBAC Supervisor Company",
                "national_id": "9988776655",
                "company_type": "COMMERCIAL",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_trade_supervisor_can_create_registration_order(self):
        from apps.companies.models import Company

        company = Company.objects.create(
            name="RBAC Supervisor Order Company",
            national_id="8877665544",
            company_type="COMMERCIAL",
        )

        user = self.create_user_with_role(
            "trade-supervisor-order-user",
            "TRADE_SUPERVISOR",
        )

        self.client.force_authenticate(
            user=user,
        )

        response = self.client.post(
            "/api/trade/registration-orders/",
            {
                "company": str(company.pk),
                "order_number": "RBAC-SUP-001",
                "registered_amount": "100000",
                "currency": "USD",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_trade_roles_do_not_have_delete_permissions(self):
        trade_roles = (
            "TRADE_VIEWER",
            "TRADE_OPERATOR",
            "TRADE_SUPERVISOR",
        )

        for role_name in trade_roles:
            user = self.create_user_with_role(
                f"{role_name.lower()}-delete-test",
                role_name,
            )

            delete_permissions = {
                permission
                for permission in user.get_all_permissions()
                if ".delete_" in permission
            }

            self.assertEqual(
                delete_permissions,
                set(),
                f"{role_name} unexpectedly has delete permissions.",
            )

    def test_security_admin_cannot_access_trade_data(self):
        user = self.create_user_with_role(
            "security-admin-user",
            "SECURITY_ADMIN",
        )

        self.client.force_authenticate(
            user=user,
        )

        response = self.client.get(
            "/api/trade/registration-orders/",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_trade_viewer_can_access_dashboard(self):
        user = self.create_user_with_role(
            "trade-viewer-dashboard-user",
            "TRADE_VIEWER",
        )

        self.client.force_authenticate(
            user=user,
        )

        response = self.client.get(
            "/api/trade/dashboard/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_security_admin_cannot_access_dashboard(self):
        user = self.create_user_with_role(
            "security-admin-dashboard-user",
            "SECURITY_ADMIN",
        )

        self.client.force_authenticate(
            user=user,
        )

        response = self.client.get(
            "/api/trade/dashboard/",
        )

        self.assertEqual(
            response.status_code,
            403,
        )