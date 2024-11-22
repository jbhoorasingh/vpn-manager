from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, Div
from .models import TunnelRequest, NetworkCIDR, TunnelValidation, Site
from .validators import validate_network_cidr

class NetworkCIDRForm(forms.ModelForm):
    class Meta:
        model = NetworkCIDR
        fields = ['cidr']
        widgets = {
            'cidr': forms.TextInput(attrs={'class': 'form-control'})
        }

class TunnelRequestForm(forms.ModelForm):
    local_networks = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter one CIDR per line (e.g., 192.168.1.0/24)'
        }),
        help_text='Enter one CIDR per line (e.g., 192.168.1.0/24)'
    )
    remote_networks = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter one CIDR per line (e.g., 10.0.0.0/8)'
        }),
        help_text='Enter one CIDR per line (e.g., 10.0.0.0/8)'
    )
        
    class Meta:
        model = TunnelRequest
        fields = [
            'business_unit', 'use_case', 'service_owner', 'notification_dl',
            'partner_name', 'technical_poc_name', 'technical_poc_email',
            'technical_poc_phone', 'support_desk_email', 'support_desk_phone',
            'site', 'ike_version', 'pre_shared_key', 'peer_gateway',
            'phase1_encryption', 'phase1_authentication', 'phase1_dh_group',
            'phase1_lifetime', 'phase2_encryption', 'phase2_authentication',
            'phase2_pfs_group', 'phase2_lifetime'
        ]
        exclude = ['requester', 'status', 'network_approved_by', 'security_approved_by', 'approval_comments']
        widgets = {
            'use_case': forms.Textarea(attrs={'rows': 4}),
        }

    
    local_networks = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Enter one CIDR per line (e.g., 192.168.1.0/24)",
        required=True
    )

    remote_networks = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Enter one CIDR per line (e.g., 10.0.0.0/24)",
        required=True
    )

    def clean_local_networks(self):
        data = self.cleaned_data['local_networks']
        return [cidr.strip() for cidr in data.split('\n') if cidr.strip()]

    def clean_remote_networks(self):
        data = self.cleaned_data['remote_networks']
        return [cidr.strip() for cidr in data.split('\n') if cidr.strip()]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            
            # Create NetworkCIDR objects for local networks
            for cidr in self.cleaned_data['local_networks']:
                NetworkCIDR.objects.create(
                    tunnel_request=instance,
                    cidr=cidr,
                    is_local=True
                )
            
            # Create NetworkCIDR objects for remote networks
            for cidr in self.cleaned_data['remote_networks']:
                NetworkCIDR.objects.create(
                    tunnel_request=instance,
                    cidr=cidr,
                    is_local=False
                )
        
        return instance


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Request Details',
                Row(
                    Column('business_unit', css_class='col-md-6'),
                    Column('site', css_class='col-md-6'),
                ),
                'use_case',
                css_class='mb-4'
            ),
            Fieldset(
                'Internal Contact Information',
                Row(
                    Column('service_owner', css_class='col-md-6'),
                    Column('notification_dl', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),
            Fieldset(
                'Partner Contact Information',
                Row(
                    Column('partner_name', css_class='col-md-12'),
                ),
                Row(
                    Column('technical_poc_name', css_class='col-md-4'),
                    Column('technical_poc_email', css_class='col-md-4'),
                    Column('technical_poc_phone', css_class='col-md-4'),
                ),
                Row(
                    Column('support_desk_email', css_class='col-md-6'),
                    Column('support_desk_phone', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),
            Fieldset(
                'VPN Settings',
                Row(
                    Column('ike_version', css_class='col-md-6'),
                    Column('pre_shared_key', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),
            Fieldset(
                'Network Details',
                Row(
                    Column('local_networks', css_class='col-md-6'),
                    Column('remote_networks', css_class='col-md-6'),
                ),
                'peer_gateway',
                css_class='mb-4'
            ),
            Fieldset(
                'Phase 1 (IKE) Settings',
                Row(
                    Column('phase1_encryption', css_class='col-md-6'),
                    Column('phase1_authentication', css_class='col-md-6'),
                ),
                Row(
                    Column('phase1_dh_group', css_class='col-md-6'),
                    Column('phase1_lifetime', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),
            Fieldset(
                'Phase 2 (IPSec) Settings',
                Row(
                    Column('phase2_encryption', css_class='col-md-6'),
                    Column('phase2_authentication', css_class='col-md-6'),
                ),
                Row(
                    Column('phase2_pfs_group', css_class='col-md-6'),
                    Column('phase2_lifetime', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),
            Div(
                Submit('submit', 'Submit Request', css_class='btn-primary'),
                Div(
                    Div(
                        '<a href="{% url \'tunnel-list\' %}" class="btn btn-secondary">Cancel</a>',
                        css_class='d-inline-block'
                    ),
                    css_class='float-end'
                ),
                css_class='d-flex justify-content-between'
            )
        )

    def clean_local_networks(self):
        networks = self._clean_networks(self.cleaned_data['local_networks'])
        return networks

    def clean_remote_networks(self):
        networks = self._clean_networks(self.cleaned_data['remote_networks'])
        return networks

    def _clean_networks(self, networks_text):
        networks = [n.strip() for n in networks_text.split('\n') if n.strip()]
        for network in networks:
            try:
                validate_network_cidr(network)
            except forms.ValidationError as e:
                raise forms.ValidationError(f'Invalid network {network}: {str(e)}')
        return networks

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Clear existing networks
            NetworkCIDR.objects.filter(tunnel_request=instance).delete()
            
            # Add local networks
            for cidr in self.cleaned_data['local_networks']:
                NetworkCIDR.objects.create(
                    tunnel_request=instance,
                    cidr=cidr,
                    is_local=True
                )
            
            # Add remote networks
            for cidr in self.cleaned_data['remote_networks']:
                NetworkCIDR.objects.create(
                    tunnel_request=instance,
                    cidr=cidr,
                    is_local=False
                )
        
        return instance
    


class TunnelApprovalForm(forms.ModelForm):
    APPROVAL_CHOICES = [
        ('PENDING', 'Keep Pending'),
        ('APPROVED', 'Approve'),
        ('REJECTED', 'Reject'),
    ]

    status = forms.ChoiceField(
        choices=APPROVAL_CHOICES,
        widget=forms.RadioSelect,
        help_text="Select your approval decision"
    )
    
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text="Optional comments about your decision"
    )

    class Meta:
        model = TunnelRequest
        fields = ['status', 'comments']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'status',
            'comments',
            Div(
                Submit('submit', 'Submit Decision', css_class='btn-primary'),
                css_class='mt-3'
            )
        )

class TunnelValidationForm(forms.ModelForm):
    class Meta:
        model = TunnelValidation
        fields = ['business_justification']
        widgets = {
            'business_justification': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'business_justification',
            Div(
                Submit('submit', 'Validate Tunnel', css_class='btn-primary'),
                css_class='mt-3'
            )
        )
    class Meta:
        model = TunnelValidation
        fields = ['business_justification']
        widgets = {
            'business_justification': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Please provide business justification for maintaining this VPN tunnel'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'business_justification',
            Div(
                Submit('submit', 'Submit Validation', css_class='btn-primary'),
                Div(
                    Div(
                        '<a href="{% url \'tunnel-list\' %}" class="btn btn-secondary">Cancel</a>',
                        css_class='d-inline-block'
                    ),
                    css_class='float-end'
                ),
                css_class='d-flex justify-content-between mt-3'
            )
        )

    def clean_business_justification(self):
        justification = self.cleaned_data['business_justification']
        if len(justification.strip()) < 10:
            raise forms.ValidationError('Business justification must be at least 10 characters long')
        return justification