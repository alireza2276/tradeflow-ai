from rest_framework import viewsets

from apps.companies.models import Company
from apps.companies.serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    search_fields = (
        "name",
        "national_id",
    )

    ordering_fields = (
        "name",
        "created_at",
    )