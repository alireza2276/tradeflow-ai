from django.core.management.base import BaseCommand

from apps.notifications.services.deadline_notification_service import (
    process_deadline_notifications,
)


class Command(BaseCommand):
    help = "Process deadline notifications for currency purchases."

    def handle(self, *args, **options):
        result = process_deadline_notifications()

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed: {result['processed_count']} | "
                f"Sent: {result['sent_count']}"
            )
        )