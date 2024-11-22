from rest_framework import serializers
from ..models import TunnelRequest, NetworkCIDR, TunnelValidation, Site

class NetworkCIDRSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkCIDR
        fields = ['cidr', 'is_local']

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'location']

class TunnelRequestSerializer(serializers.ModelSerializer):
    local_networks = NetworkCIDRSerializer(many=True, read_only=True)
    remote_networks = NetworkCIDRSerializer(many=True, read_only=True)
    site = SiteSerializer(read_only=True)
    site_id = serializers.PrimaryKeyRelatedField(
        queryset=Site.objects.filter(is_active=True),
        write_only=True,
        source='site'
    )
    local_networks_list = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    remote_networks_list = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = TunnelRequest
        fields = [
            'id', 'business_unit', 'use_case', 'service_owner',
            'notification_dl', 'status', 'phase1_encryption',
            'phase1_authentication', 'phase1_dh_group', 'phase1_lifetime',
            'phase2_encryption', 'phase2_authentication', 'phase2_pfs_group',
            'phase2_lifetime', 'peer_gateway', 'site', 'site_id',
            'local_networks', 'remote_networks', 'local_networks_list',
            'remote_networks_list', 'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def create(self, validated_data):
        local_networks = validated_data.pop('local_networks_list', [])
        remote_networks = validated_data.pop('remote_networks_list', [])
        
        tunnel = TunnelRequest.objects.create(**validated_data)
        
        # Create local networks
        for cidr in local_networks:
            NetworkCIDR.objects.create(
                tunnel_request=tunnel,
                cidr=cidr,
                is_local=True
            )
        
        # Create remote networks
        for cidr in remote_networks:
            NetworkCIDR.objects.create(
                tunnel_request=tunnel,
                cidr=cidr,
                is_local=False
            )
        
        return tunnel

class TunnelValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TunnelValidation
        fields = ['business_justification']

    def validate_business_justification(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                'Business justification must be at least 10 characters long'
            )
        return value