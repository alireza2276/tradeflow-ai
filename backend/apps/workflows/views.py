from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)

from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)
from rest_framework.response import Response

from apps.workflows.models import ApprovalRequest
from apps.workflows.serializers import (
    ApprovalRejectSerializer,
    ApprovalRequestSerializer,
)
from apps.workflows.services.approval_service import (
    approve_request,
    reject_request,
)


class CanReviewApprovalRequests(
    permissions.BasePermission
):
    message = (
        "You do not have permission to review "
        "approval requests."
    )

    def has_permission(
        self,
        request,
        view,
    ):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.has_perm(
                "workflows.review_approvalrequest"
            )
        )


class ApprovalRequestViewSet(
    viewsets.ReadOnlyModelViewSet
):
    permission_classes = (
        CanReviewApprovalRequests,
    )

    serializer_class = (
        ApprovalRequestSerializer
    )

    queryset = (
        ApprovalRequest.objects
        .select_related(
            "maker",
            "checker",
        )
        .all()
        .order_by("-created_at")
    )

    def get_queryset(self):
        queryset = super().get_queryset()

        requested_status = (
            self.request.query_params.get(
                "status"
            )
        )

        if requested_status:
            valid_statuses = {
                ApprovalRequest.Status.PENDING,
                ApprovalRequest.Status.APPROVED,
                ApprovalRequest.Status.REJECTED,
            }

            if requested_status not in valid_statuses:
                raise DRFValidationError(
                    {
                        "status": (
                            "Invalid approval request status."
                        )
                    }
                )

            return queryset.filter(
                status=requested_status
            )

        return queryset.filter(
            status=ApprovalRequest.Status.PENDING
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
    )
    def approve(
        self,
        request,
        pk=None,
    ):
        approval_request = self.get_object()

        try:
            result = approve_request(
                approval_request=approval_request,
                checker=request.user,
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(
                {
                    "detail": exc.messages,
                }
            )

        serializer = self.get_serializer(
            result
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reject",
    )
    def reject(
        self,
        request,
        pk=None,
    ):
        input_serializer = (
            ApprovalRejectSerializer(
                data=request.data
            )
        )

        input_serializer.is_valid(
            raise_exception=True
        )

        approval_request = self.get_object()

        try:
            result = reject_request(
                approval_request=approval_request,
                checker=request.user,
                reason=input_serializer.validated_data[
                    "reason"
                ],
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(
                {
                    "detail": exc.messages,
                }
            )

        output_serializer = (
            self.get_serializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )