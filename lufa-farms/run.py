import os
import time
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("lufa_farms")

def get_config():
    """Read configuration from Home Assistant options."""
    # In HA Add-ons, options are typically in /data/options.json
    # But for simplicity or env vars, we'll start with a placeholder or standard HA path
    options_path = '/data/options.json'
    if os.path.exists(options_path):
        import json
        with open(options_path, 'r') as f:
            return json.load(f)
    return {}

def main():
    logger.info("Starting Lufa Farms Add-on")
    
    config = get_config()
    email = config.get('email')
    password = config.get('password')
    
    if not email or not password:
        logger.error("Email and password must be provided in configuration.")
        sys.exit(1)
        
    client = LufaClient(email, password)
    
    # Scan interval in seconds (default 15 mins)
    scan_interval = config.get('scan_interval', 900)
    
    supervisor_token = os.environ.get('SUPERVISOR_TOKEN')
    
    while True:
        try:
            logger.info("Fetching update...")
            order_id = client.get_current_order_id()
            
            if order_id:
                logger.info(f"Found active Order ID: {order_id}")
                details = client.get_order_details(order_id)
                if details:
                    logger.info("Order details retrieved successfully.")
                    status = details.get('status')
                    eta = details.get('eta')
                    stops = details.get('stops_before')
                    amount = details.get('order_amount')
                    
                    logger.info(f"Status: {status}, ETA: {eta}, Amount: {amount}")
                    
                    if supervisor_token:
                        publish_sensor("sensor.lufa_order_status", status, {"friendly_name": "Lufa Order Status", "icon": "mdi:truck-delivery"}, supervisor_token)
                        publish_sensor("sensor.lufa_order_eta", eta, {"friendly_name": "Lufa Order ETA", "icon": "mdi:clock-outline"}, supervisor_token)
                        publish_sensor("sensor.lufa_stops_before", stops, {"friendly_name": "Lufa Stops Before", "icon": "mdi:map-marker-path"}, supervisor_token)
                        publish_sensor("sensor.lufa_order_amount", amount, {"friendly_name": "Lufa Order Amount", "icon": "mdi:cash"}, supervisor_token)
                        publish_sensor("sensor.lufa_order_id", order_id, {"friendly_name": "Lufa Order ID"}, supervisor_token)
                    else:
                        logger.warning("No SUPERVISOR_TOKEN found. Skipping HA publication.")
            else:
                logger.info("No active order found.")
                if supervisor_token:
                     publish_sensor("sensor.lufa_order_status", "No Active Order", {"friendly_name": "Lufa Order Status"}, supervisor_token)
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            
        logger.info(f"Sleeping for {scan_interval} seconds...")
        time.sleep(scan_interval)

def publish_sensor(entity_id, state, attributes, token):
    """Publishes a state to Home Assistant via the Supervisor API."""
    url = f"http://supervisor/core/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "state": str(state),
        "attributes": attributes
    }
    
    try:
        import requests
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.debug(f"Published {entity_id}: {state}")
    except Exception as e:
        logger.error(f"Failed to publish {entity_id}: {e}")

if __name__ == "__main__":
    main()
