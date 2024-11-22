from django.conf import settings
from netmiko import ConnectHandler
from .models import TunnelRequest

class FirewallManager:
    def __init__(self, firewall):
        self.firewall = firewall
        self.device = {
            'device_type': 'paloalto_panos',
            'host': firewall.hostname,
            'username': firewall.username,
            'password': firewall.password,
        }

    def push_tunnel_config(self, tunnel: TunnelRequest) -> bool:
        try:
            with ConnectHandler(**self.device) as net_connect:
                commands = self._generate_vpn_commands(tunnel)
                output = net_connect.send_config_set(commands)
                net_connect.commit()
                return True
        except Exception as e:
            raise Exception(f"Failed to configure VPN tunnel: {str(e)}")

    def _generate_vpn_commands(self, tunnel: TunnelRequest) -> list:
        tunnel_name = f"{tunnel.business_unit}-vpn"
        commands = [
            f"set network ike gateway {tunnel_name} authentication pre-shared-key key {settings.VPN_PSK}",
            f"set network ike gateway {tunnel_name} protocol-version ikev2",
            f"set network ike gateway {tunnel_name} local-address interface {self.firewall.interface}",
            f"set network ike gateway {tunnel_name} peer-address {tunnel.peer_gateway}",
            f"set network ike gateway {tunnel_name} encryption {tunnel.phase1_encryption}",
            f"set network ike gateway {tunnel_name} dh-group group{tunnel.phase1_dh_group}",
            f"set network ike gateway {tunnel_name} authentication hash {tunnel.phase1_authentication}",
            f"set network ike gateway {tunnel_name} lifetime {tunnel.phase1_lifetime}",
            
            f"set network ipsec ipsec-crypto {tunnel_name} encryption {tunnel.phase2_encryption}",
            f"set network ipsec ipsec-crypto {tunnel_name} authentication {tunnel.phase2_authentication}",
            f"set network ipsec ipsec-crypto {tunnel_name} dh-group group{tunnel.phase2_pfs_group}",
            f"set network ipsec ipsec-crypto {tunnel_name} lifetime {tunnel.phase2_lifetime}",
            
            f"set network tunnel ipsec {tunnel_name} auto-key ike-gateway {tunnel_name}",
            f"set network tunnel ipsec {tunnel_name} auto-key ipsec-crypto {tunnel_name}",
            f"set network tunnel ipsec {tunnel_name} tunnel-interface {self.firewall.tunnel_interface}",
        ]

        # Add local network routes
        for network in tunnel.local_networks.all():
            commands.append(
                f"set network virtual-router default routing-table ip static-route {tunnel_name}-local-{network.id} "
                f"destination {network.cidr} interface {self.firewall.interface}"
            )

        # Add remote network routes
        for network in tunnel.remote_networks.all():
            commands.append(
                f"set network virtual-router default routing-table ip static-route {tunnel_name}-remote-{network.id} "
                f"destination {network.cidr} interface {self.firewall.tunnel_interface}"
            )

        return commands