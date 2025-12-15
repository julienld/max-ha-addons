import os
import json
import time
import logging
import sys
from client import LufaClient
from mqtt_client import LufaMQTTClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("lufa_farms")

def get_config():
    """Read configuration from Home Assistant options."""
    options_path = '/data/options.json'
    if os.path.exists(options_path):
        import json
        with open(options_path, 'r') as f:
            return json.load(f)
    return {}

def main():
    logger.info("Starting Lufa Farms Add-on")
    
    # DEBUG: Log available environment variables
    logger.info(f"Environment variables: {list(os.environ.keys())}")
    if 'SUPERVISOR_TOKEN' in os.environ:
        logger.info("SUPERVISOR_TOKEN is present.")
    else:
        logger.warning("SUPERVISOR_TOKEN is MISSING.")
        
    if 'HASSIO_TOKEN' in os.environ:
        logger.info("HASSIO_TOKEN is present.")
        
    config = get_config()
    email = config.get('email')
    password = config.get('password')
    
    if not email or not password:
        logger.error("Email and password must be provided in configuration.")
        sys.exit(1)
        
    # Initialize Lufa Client
    lufa_client = LufaClient(email, password)
    
    # Initialize MQTT Client
    mqtt_client = LufaMQTTClient(config)
    if not mqtt_client.connect():
        logger.warning("Continuing without MQTT (Check configuration or broker status).")
    
    # Scan interval in seconds (default 15 mins)
    scan_interval = config.get('scan_interval', 900)
    
    while True:
        try:
            logger.info("Fetching update...")
            order_id = lufa_client.get_current_order_id()
            
            if order_id:
                logger.info(f"Found active Order ID: {order_id}")
                details = lufa_client.get_order_details(order_id)
                if details:
                    logger.info("Order details retrieved successfully.")
                    status = details.get('status')
                    eta = details.get('eta')
                    amount = details.get('order_amount')
                    
                    logger.info(f"Status: {status}, ETA: {eta}, Amount: {amount}")
                    
                    # Publish via MQTT
                    mqtt_client.publish_state(details, order_id)

            else:
                logger.info("No active order found.")
                # Optionally clear state or publish empty/idle state
                # mqtt_client.publish_state({'status': 'No Active Order'}, None)
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            
        logger.info(f"Sleeping for {scan_interval} seconds...")
        time.sleep(scan_interval)

if __name__ == "__main__":
    main()
