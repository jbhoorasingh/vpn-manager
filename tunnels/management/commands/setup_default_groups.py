from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tunnels.models import TunnelRequest

class Command(BaseCommand):
    help = 'Creates default groups and assigns permissions'

    def handle(self, *args, **options):
        # Get content type for TunnelRequest model
        tunnel_content_type = ContentType.objects.get_for_model(TunnelRequest)
        
        # Create Security Admin group
        security_group, security_created = Group.objects.get_or_create(name='Security_Admin')
        if security_created:
            # Add permissions for security admin
            can_approve = Permission.objects.get(
                codename='can_approve_tunnel',
                content_type=tunnel_content_type
            )
            security_group.permissions.add(can_approve)
            self.stdout.write(self.style.SUCCESS('Successfully created Security_Admin group'))
        else:
            self.stdout.write(self.style.WARNING('Security_Admin group already exists'))

        # Create Network Admin group
        network_group, network_created = Group.objects.get_or_create(name='Network_Admin')
        if network_created:
            # Add permissions for network admin
            can_approve = Permission.objects.get(
                codename='can_approve_tunnel',
                content_type=tunnel_content_type
            )
            can_push = Permission.objects.get(
                codename='can_push_to_firewall',
                content_type=tunnel_content_type
            )
            network_group.permissions.add(can_approve, can_push)
            self.stdout.write(self.style.SUCCESS('Successfully created Network_Admin group'))
        else:
            self.stdout.write(self.style.WARNING('Network_Admin group already exists'))

        self.stdout.write(self.style.SUCCESS('Groups setup completed'))