from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


TABLES = [
    "notification_deliveries",
    "notification_logs",
    "notification_recipients",
    "audit_events",
    "invoices",
    "deadline_extensions",
    "customs_clearances",
    "regulatory_deadlines",
    "shipment_parts",
    "currency_purchases",
    "payment_instruments",
    "registration_orders",
    "approval_requests",
    "companies",
]

# Intentionally preserved:
# - auth/user/account tables
# - groups, roles and permissions
# - django migrations/content types/admin metadata
# - regulatory_rules (Rule Engine configuration needed for new purchases)
# - django_session (so the current login is not forcibly invalidated)


class Command(BaseCommand):
    help = (
        "Reset TradeFlowAI demo/business data while preserving users, RBAC, "
        "migrations and regulatory rules."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show row counts only; do not delete anything.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Required for the destructive reset.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "Refusing to reset data because DEBUG=False. "
                "This command is for local/demo environments only."
            )

        if connection.vendor != "postgresql":
            raise CommandError(
                f"Unsupported database vendor: {connection.vendor}. "
                "This reset command is intentionally PostgreSQL-only."
            )

        existing_tables = set(connection.introspection.table_names())
        missing = [table for table in TABLES if table not in existing_tables]
        if missing:
            raise CommandError(
                "Expected tables are missing: " + ", ".join(missing)
            )

        counts = {}
        with connection.cursor() as cursor:
            for table in TABLES:
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                counts[table] = cursor.fetchone()[0]

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("TradeFlowAI reset summary"))
        self.stdout.write("-" * 58)
        for table in TABLES:
            self.stdout.write(f"{table:32} {counts[table]:>10}")
        self.stdout.write("-" * 58)
        self.stdout.write(f"{'TOTAL':32} {sum(counts.values()):>10}")
        self.stdout.write("")

        self.stdout.write(self.style.SUCCESS("PRESERVED:"))
        self.stdout.write("  Users/accounts")
        self.stdout.write("  Groups / roles / permissions / RBAC")
        self.stdout.write("  Regulatory rules")
        self.stdout.write("  Migrations and database schema")
        self.stdout.write("  Current Django sessions")
        self.stdout.write("")

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN ONLY: nothing was deleted."
                )
            )
            return

        if not options["confirm"]:
            raise CommandError(
                "Nothing deleted. Review --dry-run first, then run again "
                "with --confirm."
            )

        quoted_tables = ", ".join(f'"{table}"' for table in TABLES)

        # One PostgreSQL TRUNCATE statement handles the FK graph atomically.
        # AuditEvent deliberately blocks ORM deletion, so this maintenance
        # command uses SQL only inside an atomic transaction.
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {quoted_tables}")

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"RESET COMPLETE: deleted {sum(counts.values())} "
                "business/demo rows."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Users, RBAC and regulatory rules were preserved."
            )
        )
