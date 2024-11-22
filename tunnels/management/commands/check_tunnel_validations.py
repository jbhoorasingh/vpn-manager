from django.core.management.base import BaseCommand
from django.utils import timezone
from tunnels.models import TunnelRequest, TunnelValidation
from datetime import timedelta

class Command(BaseCommand):
    help = 'Check tunnel validations and send notifications for pending validations'

    def handle(self, *args, **options):
        # Find tunnels needing validation
        thirty_days_from_now = timezone.now() + timedelta(days=30)
        
        # Get tunnels with validations expiring soon
        expiring_validations = TunnelValidation.objects.filter(
            status='VALIDATED',
            next_validation_date__lte=thirty_days_from_now,
            notification_sent=False
        )

        for validation in expiring_validations:
            tunnel = validation.tunnel_request
            tunnel.create_validation_request()
            validation.notification_sent = True
            validation.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Sent validation request for tunnel {tunnel.id}')
            )

        # Mark expired validations
        expired_validations = TunnelValidation.objects.filter(
            status='PENDING',
            next_validation_date__lt=timezone.now()
        )

        for validation in expired_validations:
            validation.status = 'EXPIRED'
            validation.save()
            
            tunnel = validation.tunnel_request
            tunnel.status = 'EXPIRED'
            tunnel.save()
            
            self.stdout.write(
                self.style.WARNING(f'Marked tunnel {tunnel.id} as expired')
            )