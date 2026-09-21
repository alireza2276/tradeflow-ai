import sys
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from apps.notifications.services.sms_service import (
    DisabledSMSProvider,
    KavenegarSMSProvider,
    MockSMSProvider,
    get_sms_provider,
)


class FakeAPIException(Exception):
    pass


class FakeHTTPException(Exception):
    pass


class SMSProviderFactoryTests(SimpleTestCase):
    @override_settings(SMS_ENABLED=False, SMS_PROVIDER="KAVENEGAR")
    def test_disabled_flag_wins(self):
        self.assertIsInstance(get_sms_provider(), DisabledSMSProvider)

    @override_settings(SMS_ENABLED=True, SMS_PROVIDER="MOCK")
    def test_mock_provider(self):
        self.assertIsInstance(get_sms_provider(), MockSMSProvider)

    @override_settings(
        SMS_ENABLED=True,
        SMS_PROVIDER="KAVENEGAR",
        KAVENEGAR_API_KEY="test-key",
        KAVENEGAR_SENDER="",
        KAVENEGAR_TIMEOUT=10,
    )
    def test_kavenegar_provider(self):
        self.assertIsInstance(get_sms_provider(), KavenegarSMSProvider)


class KavenegarSMSProviderTests(SimpleTestCase):
    @override_settings(
        KAVENEGAR_API_KEY="test-key",
        KAVENEGAR_SENDER="100000",
        KAVENEGAR_TIMEOUT=7,
    )
    def test_success_returns_provider_message_id(self):
        captured = {}

        class FakeKavenegarAPI:
            def __init__(self, api_key, timeout=10):
                captured["api_key"] = api_key
                captured["timeout"] = timeout

            def sms_send(self, params):
                captured["params"] = params
                return [{"messageid": 123456789}]

        fake_module = SimpleNamespace(
            KavenegarAPI=FakeKavenegarAPI,
            APIException=FakeAPIException,
            HTTPException=FakeHTTPException,
        )

        with patch.dict(sys.modules, {"kavenegar": fake_module}):
            result = KavenegarSMSProvider().send(
                phone_number="09120000000",
                message="TradeFlowAI test",
            )

        self.assertTrue(result.success)
        self.assertEqual(result.provider, "KAVENEGAR")
        self.assertEqual(result.message_id, "123456789")
        self.assertEqual(captured["api_key"], "test-key")
        self.assertEqual(captured["timeout"], 7)
        self.assertEqual(captured["params"]["sender"], "100000")
        self.assertEqual(captured["params"]["receptor"], "09120000000")

    @override_settings(
        KAVENEGAR_API_KEY="test-key",
        KAVENEGAR_SENDER="",
        KAVENEGAR_TIMEOUT=10,
    )
    def test_api_error_is_a_failed_result(self):
        class FakeKavenegarAPI:
            def __init__(self, api_key, timeout=10):
                pass

            def sms_send(self, params):
                raise FakeAPIException("provider rejected request")

        fake_module = SimpleNamespace(
            KavenegarAPI=FakeKavenegarAPI,
            APIException=FakeAPIException,
            HTTPException=FakeHTTPException,
        )

        with patch.dict(sys.modules, {"kavenegar": fake_module}):
            result = KavenegarSMSProvider().send(
                phone_number="09120000000",
                message="TradeFlowAI test",
            )

        self.assertFalse(result.success)
        self.assertEqual(result.provider, "KAVENEGAR")
        self.assertIn("provider rejected request", result.error)

    @override_settings(
        KAVENEGAR_API_KEY="test-key",
        KAVENEGAR_SENDER="",
        KAVENEGAR_TIMEOUT=10,
    )
    def test_missing_message_id_is_not_marked_sent(self):
        class FakeKavenegarAPI:
            def __init__(self, api_key, timeout=10):
                pass

            def sms_send(self, params):
                return [{}]

        fake_module = SimpleNamespace(
            KavenegarAPI=FakeKavenegarAPI,
            APIException=FakeAPIException,
            HTTPException=FakeHTTPException,
        )

        with patch.dict(sys.modules, {"kavenegar": fake_module}):
            result = KavenegarSMSProvider().send(
                phone_number="09120000000",
                message="TradeFlowAI test",
            )

        self.assertFalse(result.success)
        self.assertIn("no message id", result.error.lower())
