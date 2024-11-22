from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import TunnelRequest, TunnelValidation

@receiver(post_save, sender=TunnelRequest)
def create_initial_validation(sender, instance, created, **kwargs):
    """Create initial validation record when tunnel is first created"""
    if created:
        TunnelValidation.objects.create(
            tunnel_request=instance,
            next_validation_date=timezone.now() + timezone.timedelta(days=365)
        )

@receiver(post_save, sender=TunnelRequest)
def notify_approvers(sender, instance, created, **kwargs):
    """Send notifications to approvers when a new tunnel request is created"""
    if created and not settings.DEBUG:  # Only send emails in production
        subject = f'New VPN Tunnel Request #{instance.id} Requires Approval'
        context = {
            'tunnel': instance,
            'created_by': instance.requester.get_full_name() or instance.requester.username,
        }
        
        # Notify network team
        network_message = render_to_string('tunnels/email/network_approval_needed.html', context)
        try:
            send_mail(
                subject=subject,
                message=network_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.notification_dl],
                html_message=network_message,
                fail_silently=True
            )
        except Exception as e:
            print(f"Failed to send email notification: {str(e)}")

@receiver(pre_save, sender=TunnelRequest)
def handle_status_change(sender, instance, **kwargs):
    """Handle status changes and notifications"""
    if not instance.pk or settings.DEBUG:  # Skip for new instances or in development
        return
        
    try:
        old_instance = TunnelRequest.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            subject = f'VPN Tunnel Request #{instance.id} Status Update'
            context = {
                'tunnel': instance,
                'old_status': old_instance.get_status_display(),
                'new_status': instance.get_status_display(),
            }
            
            message = render_to_string('tunnels/email/status_update.html', context)
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.notification_dl],
                html_message=message,
                fail_silently=True
            )
    except Exception as e:
        print(f"Failed to send status update email: {str(e)}")

@receiver(post_save, sender=TunnelValidation)
def handle_validation_status(sender, instance, **kwargs):
    """Handle validation status changes"""
    if instance.status == 'VALIDATED':
        # Update tunnel status if validated
        instance.tunnel_request.status = 'IMPLEMENTED'
        instance.tunnel_request.save()
    elif instance.status == 'EXPIRED':
        # Update tunnel status if validation expired
        instance.tunnel_request.status = 'EXPIRED'
        instance.tunnel_request.save()