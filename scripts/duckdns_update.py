"""
DuckDNS Dynamic DNS Update Script
Keeps your DuckDNS subdomain pointed to your current IP address
"""

import requests
import time
import logging
from pathlib import Path

# Configuration
DUCKDNS_DOMAIN = "your-subdomain"  # Change this to your DuckDNS subdomain (without .duckdns.org)
DUCKDNS_TOKEN = "your-token-here"  # Get this from duckdns.org after signing in
UPDATE_INTERVAL = 300  # Update every 5 minutes (in seconds)

# Setup logging
log_file = Path(__file__).parent.parent / "logs" / "duckdns.log"
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def get_current_ip():
    """Get current public IP address"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        return response.json()['ip']
    except Exception as e:
        logging.error(f"Failed to get current IP: {e}")
        return None

def update_duckdns(domain, token):
    """Update DuckDNS with current IP"""
    try:
        url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ip="
        response = requests.get(url, timeout=10)
        
        if response.text.strip() == "OK":
            current_ip = get_current_ip()
            logging.info(f"✅ DuckDNS updated successfully - IP: {current_ip}")
            return True
        else:
            logging.error(f"❌ DuckDNS update failed: {response.text}")
            return False
    except Exception as e:
        logging.error(f"❌ Error updating DuckDNS: {e}")
        return False

def main():
    """Main loop to keep DuckDNS updated"""
    logging.info("🦆 DuckDNS Update Service Started")
    logging.info(f"Domain: {DUCKDNS_DOMAIN}.duckdns.org")
    logging.info(f"Update Interval: {UPDATE_INTERVAL} seconds")
    
    if DUCKDNS_DOMAIN == "your-subdomain" or DUCKDNS_TOKEN == "your-token-here":
        logging.error("⚠️  Please configure DUCKDNS_DOMAIN and DUCKDNS_TOKEN in this script!")
        return
    
    # Initial update
    update_duckdns(DUCKDNS_DOMAIN, DUCKDNS_TOKEN)
    
    # Continuous updates
    try:
        while True:
            time.sleep(UPDATE_INTERVAL)
            update_duckdns(DUCKDNS_DOMAIN, DUCKDNS_TOKEN)
    except KeyboardInterrupt:
        logging.info("🛑 DuckDNS Update Service Stopped")

if __name__ == "__main__":
    main()
































