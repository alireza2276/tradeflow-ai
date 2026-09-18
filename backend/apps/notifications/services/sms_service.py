import uuid
from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class SMSResult:
    success: bool
    provider: str
    message_id: str = ""
    error: str = ""


class MockSMSProvider:
    """Safe default. Never sends a real SMS."""

    name = "MOCK"

    def send(self, *, phone_number: str, message: str) -> SMSResult:
        return SMSResult(
            success=True,
            provider=self.name,
            message_id=f"mock-{uuid.uuid4()}",
        )


class DisabledSMSProvider:
    name = "DISABLED"

    def send(self, *, phone_number: str, message: str) -> SMSResult:
        return SMSResult(success=False, provider=self.name, error="SMS delivery is disabled.")


def get_sms_provider():
    """Provider factory.

    V1 intentionally ships with MOCK/DISABLED only. A real provider adapter
    (for example IPPanel) is added only after credentials, sender/pattern and
    recipient policy are approved. This prevents accidental customer SMS.
    """
    if not getattr(settings, "SMS_ENABLED", False):
        return DisabledSMSProvider()

    provider = getattr(settings, "SMS_PROVIDER", "MOCK").upper()
    if provider == "MOCK":
        return MockSMSProvider()

    raise RuntimeError(f"Unsupported SMS provider: {provider}")
