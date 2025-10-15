# mpgepmc/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Donation
from .views import EmailThread # We can reuse the EmailThread class from views

@receiver(post_save, sender=Donation)
def send_status_update_email(sender, instance, created, **kwargs):
    """
    Send an email to the user when their donation status is updated
    by an admin to 'Completed' or 'Failed'.
    """
    # We only want to run this on an update, not on creation
    if not created:
        # Check if the status has actually changed
        original_status = getattr(instance, '__original_status', None)
        
        if original_status != instance.status:
            subject = ""
            html_message = ""
            
            if instance.status == 'COMPLETED':
                subject = f"Your Donation to MPG EPMC is Complete! ({instance.donation_order_number})"
                html_message = render_to_string('mpgepmc/email/donation_completed_user.html', {'donation': instance})
            
            elif instance.status == 'FAILED':
                subject = f"Update Regarding Your Donation to MPG EPMC ({instance.donation_order_number})"
                html_message = render_to_string('mpgepmc/email/donation_failed_user.html', {'donation': instance})
            
            # If a subject was set (meaning status is COMPLETED or FAILED) and the user has an email, send it
            if subject and instance.email:
                plain_message = strip_tags(html_message)
                EmailThread(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    html_message=html_message
                ).start()