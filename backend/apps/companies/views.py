from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.response import Response

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

    def destroy(self, request, *args, **kwargs):
        company = self.get_object()

        try:
            company.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "This company cannot be deleted because "
                        "it has related registration orders."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )