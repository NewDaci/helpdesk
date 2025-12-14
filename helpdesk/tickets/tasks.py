from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta

from .models import Ticket

ESCALATION_TIMES = {
    'HIGH': timedelta(hours=1),
    'MEDIUM': timedelta(hours=4),
    'LOW': timedelta(hours=24),
}

@shared_task
def escalate_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)

        if ticket.status in ['RESOLVED', 'CLOSED', 'ESCALATED']:
            return

        ticket.status = 'ESCALATED'
        ticket.save()

        send_mail(
            subject=f'Ticket Escalated: {ticket.title}',
            message=f'Ticket "{ticket.title}" has been escalated due to no response.',
            from_email='noreply@helpdesk.com',
            recipient_list=[
                ticket.created_by.email,
                'admin@helpdesk.com'
            ]
        )

    except Ticket.DoesNotExist:
        pass
