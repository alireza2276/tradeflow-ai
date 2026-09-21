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
    """Development/test provider. Never sends a real SMS."""

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
        return SMSResult(
            success=False,
            provider=self.name,
            error="SMS delivery is disabled.",
        )


class KavenegarSMSProvider:
    """Real Kavenegar adapter used by the Notification Engine."""

    name = "KAVENEGAR"

    def __init__(self):
        self.api_key = getattr(settings, "KAVENEGAR_API_KEY", "").strip()
        self.sender = getattr(settings, "KAVENEGAR_SENDER", "").strip()
        self.timeout = int(getattr(settings, "KAVENEGAR_TIMEOUT", 10))

        if not self.api_key:
            raise RuntimeError("KAVENEGAR_API_KEY is not configured.")

    @staticmethod
    def _message_id_from_response(response) -> str:
        if isinstance(response, list) and response:
            response = response[0]

        if isinstance(response, dict):
            value = (
                response.get("messageid")
                or response.get("message_id")
                or response.get("id")
            )
            return "" if value is None else str(value)

        # Defensive compatibility in case an SDK release returns an object.
        for attr in ("messageid", "message_id", "id"):
            value = getattr(response, attr, None)
            if value is not None:
                return str(value)

        return ""

    def send(self, *, phone_number: str, message: str) -> SMSResult:
        phone_number = (phone_number or "").strip()
        message = (message or "").strip()

        if not phone_number:
            return SMSResult(
                success=False,
                provider=self.name,
                error="Recipient phone number is empty.",
            )

        if not message:
            return SMSResult(
                success=False,
                provider=self.name,
                error="SMS message is empty.",
            )

        try:
            from kavenegar import APIException, HTTPException, KavenegarAPI

            api = KavenegarAPI(self.api_key, timeout=self.timeout)
            params = {
                "receptor": phone_number,
                "message": message,
            }
            if self.sender:
                params["sender"] = self.sender

            response = api.sms_send(params)
            message_id = self._message_id_from_response(response)

            if not message_id:
                return SMSResult(
                    success=False,
                    provider=self.name,
                    error="Kavenegar accepted the request but returned no message id.",
                )

            return SMSResult(
                success=True,
                provider=self.name,
                message_id=message_id,
            )

        except (APIException, HTTPException) as exc:
            return SMSResult(
                success=False,
                provider=self.name,
                error=str(exc),
            )
        except Exception as exc:
            return SMSResult(
                success=False,
                provider=self.name,
                error=f"{type(exc).__name__}: {exc}",
            )


def get_sms_provider():
    """Return the configured SMS provider.

    Real delivery is opt-in: SMS_ENABLED must be true and SMS_PROVIDER must
    explicitly be KAVENEGAR. Tests/development can continue to use MOCK.
    """

    if not getattr(settings, "SMS_ENABLED", False):
        return DisabledSMSProvider()

    provider = getattr(settings, "SMS_PROVIDER", "MOCK").strip().upper()

    if provider == "MOCK":
        return MockSMSProvider()
    if provider == "KAVENEGAR":
        return KavenegarSMSProvider()

    raise RuntimeError(f"Unsupported SMS provider: {provider}")
