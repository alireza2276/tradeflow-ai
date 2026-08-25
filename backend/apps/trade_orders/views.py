from rest_framework import viewsets

from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.serializers import RegistrationOrderSerializer


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