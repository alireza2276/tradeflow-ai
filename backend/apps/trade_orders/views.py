from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.db import transaction
from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.serializers import RegistrationOrderSerializer

from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db.models.deletion import ProtectedError


from apps.trade_orders.models import (
    CurrencyPurchase,
    PaymentInstrument,
    RegistrationOrder,
    ShipmentPart,
)

from apps.trade_orders.serializers import (
    CurrencyPurchaseSerializer,
    PaymentInstrumentSerializer,
    RegistrationOrderSerializer,
    ShipmentPartSerializer,
)

from apps.trade_orders.services.shipment_service import (
    create_shipment_part,
    update_shipment_part,
)

from apps.trade_orders.services.purchase_service import (
    create_currency_purchase,
    update_currency_purchase,
)

from apps.trade_orders.services.payment_instrument_service import (
    create_payment_instrument,
    update_payment_instrument,
)

from apps.trade_orders.services.dashboard_service import (
    get_dashboard_summary,
)

from apps.authentication.permissions import (
    CanViewTradeDashboard,
    TradeFlowModelPermissions,
)

import csv

from django.http import StreamingHttpResponse
from rest_framework.decorators import action

class RegistrationOrderViewSet(viewsets.ModelViewSet):

    permission_classes = (
        TradeFlowModelPermissions,
    )

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
        "currency",
    )

    filterset_fields = (
        "currency",
        "is_active",
    )

    ordering_fields = (
        "created_at",
        "registered_amount",
        "order_number",
    )

    @action(
        detail=False,
        methods=["get"],
        url_path="export",
    )
    def export_csv(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        class Echo:
            def write(self, value):
                return value

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        def safe_csv_value(value):
            if value is None:
                return ""

            text = str(value)

            if text.startswith(
                ("=", "+", "-", "@")
            ):
                return "'" + text

            return text

        def generate_rows():
            yield "\ufeff"

            yield writer.writerow([
                "Order Number",
                "Company",
                "National ID",
                "Registered Amount",
                "Currency",
                "Status",
            ])

            for order in queryset.iterator(
                chunk_size=1000
            ):
                yield writer.writerow([
                    safe_csv_value(
                        order.order_number
                    ),
                    safe_csv_value(
                        order.company.name
                    ),
                    safe_csv_value(
                        order.company.national_id
                    ),
                    safe_csv_value(
                        order.registered_amount
                    ),
                    safe_csv_value(
                        order.currency
                    ),
                    (
                        "Active"
                        if order.is_active
                        else "Inactive"
                    ),
                ])

        response = StreamingHttpResponse(
            generate_rows(),
            content_type=(
                "text/csv; charset=utf-8"
            ),
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; '
            'filename="registration-orders.csv"'
        )

        response[
            "X-Content-Type-Options"
        ] = "nosniff"

        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        with transaction.atomic():
            queryset = self.filter_queryset(
                self.get_queryset().select_for_update()
            )

            registration_order = get_object_or_404(
                queryset,
                pk=kwargs["pk"],
            )

            self.check_object_permissions(
                request,
                registration_order,
            )

            serializer = self.get_serializer(
                registration_order,
                data=request.data,
                partial=partial,
            )

            serializer.is_valid(
                raise_exception=True,
            )

            self.perform_update(
                serializer,
            )

            if getattr(
                    registration_order,
                    "_prefetched_objects_cache",
                    None,
            ):
                registration_order._prefetched_objects_cache = {}

            return Response(
                serializer.data
            )

    def destroy(self, request, *args, **kwargs):
        registration_order = self.get_object()

        try:
            registration_order.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "This registration order cannot be deleted "
                        "because it has related payment instruments "
                        "or currency purchases."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
class PaymentInstrumentViewSet(viewsets.ModelViewSet):

    permission_classes = (
        TradeFlowModelPermissions,
    )

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop(
            "partial",
            False,
        )

        payment_instrument = self.get_object()

        serializer = self.get_serializer(
            payment_instrument,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        data = serializer.validated_data

        registration_order = data.get(
            "registration_order",
            payment_instrument.registration_order,
        )

        if (
                registration_order.pk !=
                payment_instrument.registration_order_id
        ):
            raise DRFValidationError(
                {
                    "registration_order": (
                        "Registration order cannot be changed "
                        "after payment instrument creation."
                    )
                }
            )

        instrument_number = data.get(
            "instrument_number",
            payment_instrument.instrument_number,
        )

        try:
            updated_payment_instrument = (
                update_payment_instrument(
                    payment_instrument=payment_instrument,
                    instrument_number=instrument_number,
                )
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(
                {
                    "detail": exc.messages,
                }
            )

        output_serializer = self.get_serializer(
            updated_payment_instrument,
        )

        return Response(
            output_serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                "detail": (
                    "Payment instrument deletion is not allowed. "
                    "Use a correction or void workflow instead."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

class CurrencyPurchaseViewSet(viewsets.ModelViewSet):
    permission_classes = (
        TradeFlowModelPermissions,
    )

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

    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                "detail": (
                    "Currency purchases cannot be deleted. "
                    "Use the correction or void workflow instead."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
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

    def update(self, request, *args, **kwargs):
        return self._update_purchase(
            request=request,
            partial=False,
            *args,
            **kwargs,
        )

    def partial_update(self, request, *args, **kwargs):
        return self._update_purchase(
            request=request,
            partial=True,
            *args,
            **kwargs,
        )

    def _update_purchase(
            self,
            request,
            partial,
            *args,
            **kwargs,
    ):
        purchase = self.get_object()

        serializer = self.get_serializer(
            purchase,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        data = serializer.validated_data

        requested_currency = data.get(
            "currency",
            purchase.currency,
        )

        if requested_currency != purchase.currency:
            raise DRFValidationError(
                {
                    "currency": (
                        "Currency cannot be changed "
                        "for an existing currency purchase."
                    )
                }
            )

        registration_order = data.get(
            "registration_order",
            purchase.registration_order,
        )

        if registration_order.pk != purchase.registration_order_id:
            raise DRFValidationError(
                {
                    "registration_order": (
                        "Registration order cannot be changed "
                        "for an existing currency purchase."
                    )
                }
            )

        try:
            updated_purchase = update_currency_purchase(
                purchase=purchase,
                amount=data.get(
                    "amount",
                    purchase.amount,
                ),
                purchase_date=data.get(
                    "purchase_date",
                    purchase.purchase_date,
                ),
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(
                {"detail": exc.messages}
            )

        output_serializer = self.get_serializer(
            updated_purchase,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

class ShipmentPartViewSet(viewsets.ModelViewSet):
    permission_classes = (
        TradeFlowModelPermissions,
    )

    queryset = (
        ShipmentPart.objects
        .select_related(
            "currency_purchase",
            "currency_purchase__registration_order",
            "currency_purchase__registration_order__company",
        )
        .all()
    )

    serializer_class = ShipmentPartSerializer

    search_fields = (
        "reference_number",
        "currency_purchase__registration_order__order_number",
        "currency_purchase__registration_order__company__name",
        "currency_purchase__registration_order__company__national_id",
    )

    ordering_fields = (
        "shipment_date",
        "received_date",
        "amount",
        "created_at",
    )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        shipment = self.get_object()

        if (
                "currency_purchase" in request.data
                and str(request.data["currency_purchase"])
                != str(shipment.currency_purchase_id)
        ):
            raise DRFValidationError(
                {
                    "currency_purchase": (
                        "Currency purchase cannot be changed "
                        "for an existing shipment part."
                    )
                }
            )

        serializer = self.get_serializer(
            shipment,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        data = serializer.validated_data

        try:
            updated_shipment = update_shipment_part(
                shipment=shipment,
                amount=data.get(
                    "amount",
                    shipment.amount,
                ),
                shipment_date=data.get(
                    "shipment_date",
                    shipment.shipment_date,
                ),
                received_date=data.get(
                    "received_date",
                    shipment.received_date,
                ),
                reference_number=data.get(
                    "reference_number",
                    shipment.reference_number,
                ),
                notes=data.get(
                    "notes",
                    shipment.notes,
                ),
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(
                {"detail": exc.messages}
            )

        output_serializer = self.get_serializer(
            updated_shipment,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                "detail": (
                    "Shipment parts cannot be deleted directly. "
                    "Use the correction or void workflow instead."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
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
            shipment = create_shipment_part(
                currency_purchase=data["currency_purchase"],
                amount=data["amount"],
                shipment_date=data.get("shipment_date"),
                received_date=data.get("received_date"),
                reference_number=data.get(
                    "reference_number",
                    "",
                ),
                notes=data.get("notes", ""),
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(
                {"detail": exc.messages}
            )

        output_serializer = self.get_serializer(
            shipment,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )

class DashboardSummaryAPIView(APIView):
    permission_classes = (
        CanViewTradeDashboard,
    )

    def get(self, request):
        summary = get_dashboard_summary()

        return Response(
            summary,
            status=status.HTTP_200_OK,
        )