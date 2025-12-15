
import os
import json
import logging
import time
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

# Device Info
DEVICE_ID = "lufa_farms_account"
DEVICE_NAME = "Lufa Farms"
MANUFACTURER = "Lufa Farms"

class LufaMQTTClient:
    def __init__(self, config):
        self.config = config
        self.mqtt_client = None
        self.connected = False
        
    def connect(self):
        """Connects to the MQTT broker."""
        # Priorities:
        # 1. Manual config from options
        # 2. Service config from env vars (mqtt:want)
        
        host = self.config.get('mqtt_host')
        port = self.config.get('mqtt_port')
        username = self.config.get('mqtt_username')
        password = self.config.get('mqtt_password')
        
        # Check for service injection if manual config is missing/empty
        if not host:
            logger.info("No manual MQTT host configured. Checking for Supervisor MQTT service...")
            host = os.environ.get('MQTT_HOST')
            port = os.environ.get('MQTT_PORT')
            username = os.environ.get('MQTT_USER')
            password = os.environ.get('MQTT_PASSWORD')
            
        if not host:
            logger.warning("No MQTT configuration found. MQTT features will be disabled.")
            return False

        try:
            # Clean up port
            if port:
                port = int(port)
            else:
                port = 1883

            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="lufa_farms_addon")
            
            if username and password:
                self.mqtt_client.username_pw_set(username, password)
                
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            
            logger.info(f"Connecting to MQTT Broker at {host}:{port}...")
            self.mqtt_client.connect(host, port, 60)
            self.mqtt_client.loop_start()
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
            self.connected = True
            self._publish_discovery_config()
        else:
            logger.error(f"Failed to connect, return code {rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None): # Added properties=None for v2 compatibility
        logger.warning("Disconnected from MQTT Broker")
        self.connected = False

    def _publish_discovery_config(self):
        """Publishes Home Assistant MQTT Discovery payloads."""
        logger.info("Publishing MQTT Discovery payloads...")
        
        sensors = [
            {
                "id": "status",
                "name": "Order Status",
                "icon": "mdi:truck-delivery",
                "value_template": "{{ value_json.status }}"
            },
            {
                "id": "eta",
                "name": "ETA",
                "icon": "mdi:clock-outline",
                "value_template": "{{ value_json.eta }}"
            },
            {
                "id": "stops_before",
                "name": "Stops Before",
                "icon": "mdi:map-marker-path",
                "value_template": "{{ value_json.stops_before }}",
                "unit_of_measurement": "stops"
            },
            {
                "id": "order_amount",
                "name": "Order Amount",
                "icon": "mdi:cash",
                "value_template": "{{ value_json.order_amount }}"
            },
            {
                "id": "order_id",
                "name": "Order ID",
                "icon": "mdi:identifier",
                "value_template": "{{ value_json.order_id }}"
            }
        ]
        
        for sensor in sensors:
            unique_id = f"{DEVICE_ID}_{sensor['id']}"
            topic = f"homeassistant/sensor/{DEVICE_ID}/{sensor['id']}/config"
            
            payload = {
                "name": sensor['name'],
                "unique_id": unique_id,
                "state_topic": f"lufa_farms/{DEVICE_ID}/state",
                "value_template": sensor['value_template'],
                "icon": sensor['icon'],
                "device": {
                    "identifiers": [DEVICE_ID],
                    "name": DEVICE_NAME,
                    "manufacturer": MANUFACTURER
                }
            }
            
            if "unit_of_measurement" in sensor:
                payload["unit_of_measurement"] = sensor["unit_of_measurement"]
                
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)

    def publish_state(self, details, order_id):
        """Publishes the current state to the state topic."""
        if not self.connected or not self.mqtt_client:
            return

        topic = f"lufa_farms/{DEVICE_ID}/state"
        
        # Flatten details for easier template access if needed, or just dump it
        # We need to ensure all keys used in templates are present
        payload = {
            "status": details.get('status', 'Unknown'),
            "eta": details.get('eta', 'Unknown'),
            "stops_before": details.get('stops_before', 0),
            "order_amount": details.get('order_amount', '0.00 $'),
            "order_id": order_id
        }
        
        self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
        logger.debug(f"Published state update to {topic}")

