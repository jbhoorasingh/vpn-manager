from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import TunnelRequest, TunnelValidation
from .forms import TunnelRequestForm, TunnelApprovalForm, TunnelValidationForm
from .firewall import FirewallManager

class TunnelRequestListView(LoginRequiredMixin, ListView):
    model = TunnelRequest
    template_name = 'tunnels/tunnel_list.html'
    context_object_name = 'tunnels'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return TunnelRequest.objects.all()
        elif user.groups.filter(name='Security_Admin').exists():
            return TunnelRequest.objects.filter(
                Q(status='PENDING') | 
                Q(status='SECURITY_REVIEW') |
                Q(security_approved_by=user)
            )
        elif user.groups.filter(name='Network_Admin').exists():
            return TunnelRequest.objects.filter(
                Q(status='NETWORK_REVIEW') |
                Q(network_approved_by=user)
            )
        return TunnelRequest.objects.filter(requester=user)

class TunnelRequestCreateView(LoginRequiredMixin, CreateView):
    model = TunnelRequest
    form_class = TunnelRequestForm
    template_name = 'tunnels/tunnel_form.html'
    success_url = reverse_lazy('tunnel-list')

    def form_valid(self, form):
        form.instance.requester = self.request.user
        form.instance.status = 'SECURITY_REVIEW'  # Start with security review
        return super().form_valid(form)

class TunnelRequestDetailView(LoginRequiredMixin, DetailView):
    model = TunnelRequest
    template_name = 'tunnels/tunnel_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validation_history'] = self.object.validations.order_by('-validation_date')
        return context

class TunnelApprovalView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TunnelRequest
    form_class = TunnelApprovalForm
    template_name = 'tunnels/tunnel_approval.html'
    success_url = reverse_lazy('tunnel-list')
    permission_required = 'tunnels.can_approve_tunnel'

    def has_permission(self):
        """Check if user has appropriate permissions"""
        user = self.request.user
        tunnel = self.get_object()
        
        if user.groups.filter(name='Security_Admin').exists():
            return tunnel.status in ['PENDING', 'SECURITY_REVIEW']
        elif user.groups.filter(name='Network_Admin').exists():
            return tunnel.status == 'NETWORK_REVIEW'
        return False

    def form_valid(self, form):
        tunnel = form.instance
        new_status = form.cleaned_data['status']
        comments = form.cleaned_data.get('comments', '')
        
        if self.request.user.groups.filter(name='Security_Admin').exists():
            tunnel.security_approved_by = self.request.user
            if new_status == 'APPROVED':
                tunnel.status = 'NETWORK_REVIEW'
                messages.success(self.request, 'Security review approved. Request forwarded to network team.')
            elif new_status == 'REJECTED':
                tunnel.status = 'REJECTED'
                messages.warning(self.request, 'Request rejected by security team.')
            
        elif self.request.user.groups.filter(name='Network_Admin').exists():
            if tunnel.security_approved_by is None:
                messages.error(self.request, 'Security approval required before network review.')
                return self.form_invalid(form)
                
            tunnel.network_approved_by = self.request.user
            if new_status == 'APPROVED':
                tunnel.status = 'APPROVED'
                try:
                    firewall = FirewallManager(tunnel.site.firewall)
                    firewall.push_tunnel_config(tunnel)
                    tunnel.status = 'PROVISIONED'
                    messages.success(self.request, 'VPN tunnel approved and configured successfully.')
                except Exception as e:
                    messages.error(self.request, f'Failed to configure VPN tunnel: {str(e)}')
                    return self.form_invalid(form)
            elif new_status == 'REJECTED':
                tunnel.status = 'REJECTED'
                messages.warning(self.request, 'Request rejected by network team.')

        tunnel.approval_comments = comments
        return super().form_valid(form)

class TunnelValidationView(LoginRequiredMixin, UpdateView):
    model = TunnelValidation
    form_class = TunnelValidationForm
    template_name = 'tunnels/tunnel_validation.html'
    success_url = reverse_lazy('tunnel-list')

    def get_object(self):
        tunnel = get_object_or_404(TunnelRequest, pk=self.kwargs['pk'])
        # Check if user is authorized to validate this tunnel
        if not (self.request.user.email == tunnel.service_owner or 
                self.request.user.is_superuser):
            messages.error(self.request, 'You are not authorized to validate this tunnel.')
            return redirect('tunnel-list')
            
        validation = tunnel.current_validation
        if not validation or validation.status != 'PENDING':
            validation = tunnel.create_validation_request()
        return validation

    def form_valid(self, form):
        validation = form.instance
        validation.validated_by = self.request.user
        validation.status = 'VALIDATED'
        validation.validation_date = timezone.now()
        validation.next_validation_date = timezone.now() + timezone.timedelta(days=365)
        
        # Update tunnel status
        tunnel = validation.tunnel_request
        tunnel.status = 'IMPLEMENTED'
        tunnel.save()
        
        messages.success(self.request, 'Tunnel validation completed successfully.')
        return super().form_valid(form)