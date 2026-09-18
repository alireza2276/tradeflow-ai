from django.db.models import Q

from apps.notifications.models import NotificationRecipient


def list_recipients_for_purchase(*, purchase):
    """Architecture C: active bank recipients + contacts of this company only."""
    company = purchase.registration_order.company
    return NotificationRecipient.objects.filter(is_active=True).filter(
        Q(recipient_type=NotificationRecipient.RecipientType.BANK_USER)
        | Q(
            recipient_type=NotificationRecipient.RecipientType.COMPANY_CONTACT,
            company=company,
        )
    )
