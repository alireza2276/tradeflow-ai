from rest_framework.permissions import (
    DjangoModelPermissions,
)


class TradeFlowModelPermissions(DjangoModelPermissions):
    perms_map = {
        **DjangoModelPermissions.perms_map,
        "GET": [
            "%(app_label)s.view_%(model_name)s",
        ],
        "HEAD": [
            "%(app_label)s.view_%(model_name)s",
        ],
        "OPTIONS": [
            "%(app_label)s.view_%(model_name)s",
        ],
    }

from rest_framework.permissions import BasePermission


class CanViewTradeDashboard(BasePermission):
    message = "You do not have permission to view the trade dashboard."

    required_permissions = (
        "trade_orders.view_registrationorder",
        "trade_orders.view_currencypurchase",
    )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.has_perms(
            self.required_permissions,
        )
