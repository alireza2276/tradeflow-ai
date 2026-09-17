from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


ROLE_NAMES = (
    "TRADE_VIEWER",
    "TRADE_OPERATOR",
    "TRADE_SUPERVISOR",
    "SECURITY_ADMIN",
)


ROLE_PERMISSIONS = {
    "TRADE_VIEWER": (
        "companies.view_company",
        "documents.view_invoice",
        "notifications.view_notificationlog",
        "trade_orders.view_currencypurchase",
        "trade_orders.view_paymentinstrument",
        "trade_orders.view_registrationorder",
        "trade_orders.view_shipmentpart",
        "trade_orders.view_customsclearance",
        "trade_orders.view_deadlineextension",
        "trade_orders.view_regulatorydeadline",
    ),

    "TRADE_OPERATOR": (
        "companies.view_company",
        "documents.view_invoice",
        "documents.add_invoice",
        "documents.change_invoice",
        "notifications.view_notificationlog",
        "trade_orders.view_registrationorder",
        "trade_orders.view_paymentinstrument",
        "trade_orders.add_paymentinstrument",
        "trade_orders.change_paymentinstrument",
        "trade_orders.view_currencypurchase",
        "trade_orders.add_currencypurchase",
        "trade_orders.change_currencypurchase",
        "trade_orders.void_currencypurchase",
        "trade_orders.view_shipmentpart",
        "trade_orders.add_shipmentpart",
        "trade_orders.change_shipmentpart",
        "trade_orders.void_shipmentpart",
        "trade_orders.view_customsclearance",
        "trade_orders.add_customsclearance",
        "trade_orders.change_customsclearance",
        "trade_orders.view_regulatorydeadline",
    ),

    "TRADE_SUPERVISOR": (
        "companies.view_company",
        "companies.add_company",
        "companies.change_company",
        "documents.view_invoice",
        "documents.add_invoice",
        "documents.change_invoice",
        "notifications.view_notificationlog",
        "trade_orders.view_registrationorder",
        "trade_orders.add_registrationorder",
        "trade_orders.change_registrationorder",
        "trade_orders.view_paymentinstrument",
        "trade_orders.add_paymentinstrument",
        "trade_orders.change_paymentinstrument",
        "trade_orders.view_currencypurchase",
        "trade_orders.add_currencypurchase",
        "trade_orders.change_currencypurchase",
        "trade_orders.view_shipmentpart",
        "trade_orders.add_shipmentpart",
        "trade_orders.change_shipmentpart",
        "trade_orders.view_customsclearance",
        "trade_orders.add_customsclearance",
        "trade_orders.change_customsclearance",
        "trade_orders.view_deadlineextension",
        "trade_orders.extend_currencypurchase_deadline",
        "trade_orders.view_regulatorydeadline",
        "trade_orders.view_regulatoryrule",
        "workflows.review_approvalrequest",
        "audit.view_sensitive_audit",

    ),

    "SECURITY_ADMIN": (
        "audit.view_sensitive_audit",
        "trade_orders.view_regulatoryrule",
        "trade_orders.add_regulatoryrule",
        "trade_orders.change_regulatoryrule",
        "trade_orders.view_regulatorydeadline",
    ),
}


class Command(BaseCommand):
    help = "Create or update TradeFlowAI RBAC groups."

    def handle(self, *args, **options):
        for role_name in ROLE_NAMES:
            group, created = Group.objects.get_or_create(
                name=role_name,
            )

            permission_codes = ROLE_PERMISSIONS[role_name]

            permissions = []

            for permission_code in permission_codes:
                app_label, codename = permission_code.split(".", 1)

                permission = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename,
                )

                permissions.append(permission)

            group.permissions.set(permissions)

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created role: {group.name}"
                    )
                )
            else:
                self.stdout.write(
                    f"Updated role: {group.name}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                "RBAC groups and permissions are ready."
            )
        )
