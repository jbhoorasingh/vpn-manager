from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from datetime import timedelta
from simple_history.models import HistoricalRecords
from .validators import validate_network_cidr, validate_lifetime, validate_business_unit

class Site(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class Firewall(models.Model):
    site = models.OneToOneField(Site, on_delete=models.PROTECT, related_name='firewall')
    hostname = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)  # In production, use encrypted field
    interface = models.CharField(max_length=50, default='ethernet1/1')
    tunnel_interface = models.CharField(max_length=50, default='tunnel.1')
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.site.name} Firewall ({self.hostname})"

    class Meta:
        verbose_name = "Firewall"
        verbose_name_plural = "Firewalls"

class NetworkCIDR(models.Model):
    cidr = models.CharField(max_length=100, validators=[validate_network_cidr])
    tunnel_request = models.ForeignKey('TunnelRequest', on_delete=models.CASCADE)
    is_local = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Network CIDR"
        verbose_name_plural = "Network CIDRs"

    def __str__(self):
        return f"{self.cidr} ({'Local' if self.is_local else 'Remote'})"

class TunnelValidation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VALIDATED', 'Validated'),
        ('EXPIRED', 'Expired'),
        ('DECOMMISSIONED', 'Decommissioned'),
    ]

    tunnel_request = models.ForeignKey('TunnelRequest', on_delete=models.CASCADE, related_name='validations')
    validated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    validation_date = models.DateTimeField(auto_now_add=True)
    next_validation_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    business_justification = models.TextField(blank=True)
    notification_sent = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return f"Validation for {self.tunnel_request} - {self.validation_date.date()}"

    def save(self, *args, **kwargs):
        if not self.next_validation_date:
            self.next_validation_date = timezone.now() + timedelta(days=365)
        super().save(*args, **kwargs)

class TunnelRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SECURITY_REVIEW', 'Security Review'),
        ('NETWORK_REVIEW', 'Network Review'),
        ('APPROVED', 'Approved'),
        ('PROVISIONED', 'Provisioned'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
        ('DECOMMISSIONED', 'Decommissioned'),
    ]

    ENCRYPTION_CHOICES = [
        ('AES-256', 'AES-256'),
        ('AES-192', 'AES-192'),
        ('AES-128', 'AES-128'),
    ]

    DH_GROUP_CHOICES = [
        ('2', 'Group 2 (1024-bit)'),
        ('5', 'Group 5 (1536-bit)'),
        ('14', 'Group 14 (2048-bit)'),
    ]

    IKE_VERSION_CHOICES = [
        ('1', 'IKEv1'),
        ('2', 'IKEv2'),
    ]

    # Request Details
    requester = models.ForeignKey(User, on_delete=models.PROTECT)
    business_unit = models.CharField(max_length=100, validators=[validate_business_unit])
    use_case = models.TextField()

    # Internal Contact Details
    service_owner = models.EmailField(help_text="Internal user email of the service owner")
    notification_dl = models.EmailField(
        verbose_name="Notification Distribution List",
        help_text="Internal distribution list for notifications"
    )

    # Partner Contact Details
    partner_name = models.CharField(
        max_length=100,
        help_text="Name of the partner organization"
    )
    technical_poc_name = models.CharField(
        max_length=100,
        verbose_name="Technical Point of Contact Name"
    )
    technical_poc_email = models.EmailField(
        verbose_name="Technical Point of Contact Email"
    )
    technical_poc_phone = models.CharField(
        max_length=20,
        verbose_name="Technical Point of Contact Phone"
    )
    support_desk_email = models.EmailField(
        verbose_name="Support/Helpdesk Email",
        blank=True,
        null=True
    )
    support_desk_phone = models.CharField(
        max_length=20,
        verbose_name="Support/Helpdesk Phone",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    site = models.ForeignKey(Site, on_delete=models.PROTECT)

    # VPN Settings
    ike_version = models.CharField(max_length=1, choices=IKE_VERSION_CHOICES, default='2')
    pre_shared_key = models.CharField(max_length=255)

    # Phase 1 Settings
    phase1_encryption = models.CharField(max_length=10, choices=ENCRYPTION_CHOICES)
    phase1_authentication = models.CharField(max_length=10, default='SHA256')
    phase1_dh_group = models.CharField(max_length=2, choices=DH_GROUP_CHOICES)
    phase1_lifetime = models.IntegerField(default=28800, validators=[validate_lifetime])

    # Phase 2 Settings
    phase2_encryption = models.CharField(max_length=10, choices=ENCRYPTION_CHOICES)
    phase2_authentication = models.CharField(max_length=10, default='SHA256')
    phase2_pfs_group = models.CharField(max_length=2, choices=DH_GROUP_CHOICES)
    phase2_lifetime = models.IntegerField(default=3600, validators=[validate_lifetime])

    # Network Details
    peer_gateway = models.GenericIPAddressField()

    # Approval Details
    network_approved_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='network_approvals'
    )
    security_approved_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='security_approvals'
    )
    approval_comments = models.TextField(blank=True)
    
    history = HistoricalRecords()

    def __str__(self):
        return f"VPN Tunnel Request {self.id} - {self.business_unit}"

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("can_approve_tunnel", "Can approve tunnel requests"),
            ("can_push_to_firewall", "Can push tunnel config to firewall"),
            ("can_validate_tunnel", "Can validate tunnel annually"),
        ]

    @property
    def local_networks(self):
        return NetworkCIDR.objects.filter(tunnel_request=self, is_local=True)

    @property
    def remote_networks(self):
        return NetworkCIDR.objects.filter(tunnel_request=self, is_local=False)

    @property
    def current_validation(self):
        return self.validations.order_by('-validation_date').first()

    def create_validation_request(self):
        """Create a new validation request for the tunnel"""
        validation = TunnelValidation.objects.create(
            tunnel_request=self,
            status='PENDING'
        )
        self._send_validation_notification()
        return validation

    def _send_validation_notification(self):
        """Send email notification to service owner for tunnel validation"""
        subject = f'Annual Validation Required - VPN Tunnel {self.id}'
        message = render_to_string('tunnels/email/validation_request.html', {
            'tunnel': self,
            'validation_url': reverse('tunnel-validate', args=[self.id]),
        })
        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # Use DEFAULT_FROM_EMAIL from settings
            recipient_list=[self.notification_dl],
            html_message=message,
        )