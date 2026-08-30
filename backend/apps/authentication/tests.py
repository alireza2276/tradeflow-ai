from django.contrib.auth import get_user_model
from django.test import Client, TestCase


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