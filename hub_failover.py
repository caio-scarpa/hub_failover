# Import the required modules
import requests
import time
import logging
import os

# Configure the logging module to display messages of all severity levels
logging.basicConfig(level=logging.INFO)

# Define the API key, organization ID, and MX details
api_key = "your_api_key"
organization_id = "your_org_id"
mx_primary = {"serial": "sn_primary", "network_id": "net_id_primary", "public_ip": "primary_ip"}
mx_backup = {"serial": "sn_backup", "network_id": "net_id_backup", "public_ip": "backup_ip"}
branches = [
    {"serial": "sn_br1", "network_id": "net_id_br1"},
    {"serial": "sn_br2", "network_id": "net_id_br1"}
]

# Define the headers for the API requests
headers = {
    "X-Cisco-Meraki-API-Key": api_key,
    "Content-Type": "application/json"
}

# This function checks if a host (IP) is reachable
def is_host_reachable(ip):
    response = os.system("ping -c 5 " + ip)
    # The ping command returns 0 if the host is reachable
    if response == 0:
        return True
    else:
        return False

# This function sets the VPN configuration of a network
def set_vpn_config(network_id, vpn_config):
    url = f"https://api.meraki.com/api/v1/networks/{network_id}/appliance/vpn/siteToSiteVpn"
    try:
        response = requests.put(url, headers=headers, json=vpn_config)
        if response.status_code != 200:
            logging.error(f"Failed to set VPN config: {response.json()}")
    except Exception as e:
        logging.error(f"Failed to set VPN config: {e}")

# The main loop
while True:
    try:
        primary_reachable = is_host_reachable(mx_primary["public_ip"])
        if not primary_reachable:
            logging.info("Primary MX is down, switching to backup MX")
            vpn_config = {
                "mode": "spoke",
                "hubs": [
                    {"hubId": mx_backup["network_id"], "useVpn": True}
                ]
            }
            for branch in branches:
                set_vpn_config(branch["network_id"], vpn_config)
        else:
            logging.info("Primary MX is active")
            vpn_config = {
                "mode": "hub",
                "hubs": [
                    {"hubId": mx_primary["network_id"], "useVpn": True}
                ]
            }
            for branch in branches:
                set_vpn_config(branch["network_id"], vpn_config)
        time.sleep(20)
    except Exception as e:
        logging.error(f"An error occurred in the main loop: {e}")
        time.sleep(20)
