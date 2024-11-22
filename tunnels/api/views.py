from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from ..models import TunnelRequest, TunnelValidation
from .serializers import TunnelRequestSerializer, TunnelValidationSerializer
from ..firewall import FirewallManager

class TunnelRequestViewSet(viewsets.ModelViewSet):
    serializer_class = TunnelRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter tunnels based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return TunnelRequest.objects.all()
        elif user.groups.filter(name__in=['Network_Admin', 'Security_Admin']).exists():
            return TunnelRequest.objects.all()
        return TunnelRequest.objects.filter(requester=user)

    def perform_create(self, serializer):
        """Set requester to current user when creating tunnel request"""
        serializer.save(requester=self.request.user)

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Handle annual tunnel validation"""
        tunnel = self.get_object()
        validation_serializer = TunnelValidationSerializer(data=request.data)
        
        if validation_serializer.is_valid():
            # Create or update validation
            validation = tunnel.current_validation
            if not validation or validation.status != 'PENDING':
                validation = tunnel.create_validation_request()
            
            validation.business_justification = validation_serializer.validated_data['business_justification']
            validation.validated_by = request.user
            validation.validation_date = timezone.now()
            validation.next_validation_date = timezone.now() + timezone.timedelta(days=365)
            validation.status = 'VALIDATED'
            validation.save()
            
            return Response({'status': 'Tunnel validated successfully'})
        return Response(validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def push_to_firewall(self, request, pk=None):
        """Push tunnel configuration to firewall"""
        tunnel = self.get_object()
        
        if not request.user.has_perm('tunnels.can_push_to_firewall'):
            return Response(
                {'error': 'You do not have permission to push configurations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if tunnel.status != 'SECURITY_APPROVED':
            return Response(
                {'error': 'Tunnel must be security approved before deployment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            firewall = FirewallManager(tunnel.site.firewall)
            firewall.push_tunnel_config(tunnel)
            tunnel.status = 'IMPLEMENTED'
            tunnel.save()
            return Response({'status': 'Configuration pushed successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )