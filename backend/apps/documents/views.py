from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from apps.authentication.permissions import (
    TradeFlowModelPermissions,
)
from apps.documents.models import Invoice
from apps.documents.serializers import InvoiceSerializer
from apps.documents.services.invoice_service import create_invoice


class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = (
        TradeFlowModelPermissions,
    )

    queryset = (
        Invoice.objects
        .select_related(
            "shipment_part",
            "shipment_part__currency_purchase",
            "shipment_part__currency_purchase__registration_order",
            "shipment_part__currency_purchase__registration_order__company",
        )
        .all()
    )

    serializer_class = InvoiceSerializer

    search_fields = (
        "shipment_part__reference_number",
        "shipment_part__currency_purchase__registration_order__order_number",
        "shipment_part__currency_purchase__registration_order__company__name",
        "shipment_part__currency_purchase__registration_order__company__national_id",
    )

    ordering_fields = (
        "submission_date",
        "total_amount",
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
            invoice = create_invoice(
                shipment_part=data["shipment_part"],
                fob_amount=data["fob_amount"],
                freight_amount=data["freight_amount"],
                submission_date=data["submission_date"],
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(
                {"detail": exc.messages}
            )

        output_serializer = self.get_serializer(
            invoice,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )