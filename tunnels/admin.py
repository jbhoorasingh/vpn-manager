from django.contrib import admin
from .models import Site, Firewall, TunnelRequest, NetworkCIDR, TunnelValidation
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active')
    search_fields = ('name', 'location')
    list_filter = ('is_active',)

@admin.register(Firewall)
class FirewallAdmin(admin.ModelAdmin):
    list_display = ('site', 'hostname', 'is_active')
    search_fields = ('site__name', 'hostname')
    list_filter = ('is_active',)
    exclude = ('password',)  # Hide password in admin form

@admin.register(TunnelRequest)
class TunnelRequestAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'site', 'business_unit', 'status', 'created_at')
    list_filter = ('status', 'site', 'created_at')
    search_fields = ('business_unit', 'service_owner')
    readonly_fields = ('created_at',)

@admin.register(NetworkCIDR)
class NetworkCIDRAdmin(admin.ModelAdmin):
    list_display = ('cidr', 'tunnel_request', 'is_local')
    list_filter = ('is_local',)
    search_fields = ('cidr', 'tunnel_request__business_unit')

@admin.register(TunnelValidation)
class TunnelValidationAdmin(admin.ModelAdmin):
    list_display = ('tunnel_request', 'status', 'validation_date', 'next_validation_date')
    list_filter = ('status', 'validation_date')
    search_fields = ('tunnel_request__business_unit',)