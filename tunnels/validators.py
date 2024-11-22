from django.core.exceptions import ValidationError
from ipaddress import ip_network
import re

def validate_network_cidr(value):
    try:
        network = ip_network(value)
        if network.num_addresses < 2:
            raise ValidationError('Network must have at least 2 addresses')
    except ValueError:
        raise ValidationError('Invalid network CIDR format')

def validate_lifetime(value):
    """
    Validate IPSec lifetime values.
    Phase 1 (IKE) and Phase 2 (IPSec) lifetimes should be between 300 seconds (5 minutes)
    and 86400 seconds (24 hours).
    """
    if not isinstance(value, int):
        raise ValidationError('Lifetime must be an integer')
    
    if value < 300 or value > 86400:
        raise ValidationError('Lifetime must be between 300 and 86400 seconds (5 minutes to 24 hours)')

def validate_business_unit(value):
    """
    Validate business unit names.
    Only allow alphanumeric characters, underscores, and hyphens.
    Length must be between 2 and 50 characters.
    """
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise ValidationError('Business unit can only contain letters, numbers, underscores, and hyphens')
    
    if len(value) < 2 or len(value) > 50:
        raise ValidationError('Business unit must be between 2 and 50 characters')