from rest_framework import viewsets

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.serializers import RegistrationOrderSerializer

from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.trade_orders.models import (
    CurrencyPurchase,
    PaymentInstrument,
    RegistrationOrder,
)

from apps.trade_orders.serializers import (
    CurrencyPurchaseSerializer,
    PaymentInstrumentSerializer,
    RegistrationOrderSerializer,
)

from apps.trade_orders.services.purchase_service import (
    create_currency_purchase,
)

from apps.trade_orders.services.payment_instrument_service import (
    create_payment_instrument,
)

class RegistrationOrderViewSet(viewsets.ModelViewSet):
    queryset = (
        RegistrationOrder.objects
        .select_related("company")
        .all()
    )

    serializer_class = RegistrationOrderSerializer

    search_fields = (
        "order_number",
        "company__name",
        "company__national_id",
    )

    ordering_fields = (
        "created_at",
        "registered_amount",
        "order_number",
    )

class PaymentInstrumentViewSet(viewsets.ModelViewSet):
    queryset = (
        PaymentInstrument.objects
        .select_related(
            "registration_order",
            "registration_order__company",
        )
        .all()
    )

    serializer_class = PaymentInstrumentSerializer

    search_fields = (
        "instrument_number",
        "registration_order__order_number",
        "registration_order__company__name",
        "registration_order__company__national_id",
    )

    ordering_fields = (
        "created_at",
        "instrument_number",
    )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        registration_order = serializer.validated_data[
            "registration_order"
        ]

        instrument_number = serializer.validated_data[
            "instrument_number"
        ]

        payment_instrument = create_payment_instrument(
            registration_order=registration_order,
            instrument_number=instrument_number,
        )

        output_serializer = self.get_serializer(
            payment_instrument,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )

class CurrencyPurchaseViewSet(viewsets.ModelViewSet):
    queryset = (
        CurrencyPurchase.objects
        .select_related(
            "registration_order",
            "registration_order__company",
        )
        .all()
    )

    serializer_class = CurrencyPurchaseSerializer

    search_fields = (
        "registration_order__order_number",
        "registration_order__company__name",
        "registration_order__company__national_id",
        "currency",
    )

    ordering_fields = (
        "purchase_date",
        "deadline",
        "amount",
        "created_at",
    )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        data = serializer.validated_data

        try:
            purchase = create_currency_purchase(
                registration_order=data["registration_order"],
                amount=data["amount"],
                currency=data["currency"],
                purchase_date=data["purchase_date"],
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(
                {"detail": exc.messages}
            )

        output_serializer = self.get_serializer(
            purchase,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )