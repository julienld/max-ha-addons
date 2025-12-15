import requests
import logging
import json

logger = logging.getLogger(__name__)

BASE_URL = "https://montreal.lufa.com"
LOGIN_URL = f"{BASE_URL}/fr/login"
API_URL_ORDER_DETAILS = f"{BASE_URL}/fr/superMarket/GetUserOrderDetails"
API_URL_TRACK_ORDER = f"{BASE_URL}/fr/orders/getTrackOrderData"

class LufaClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        })
        self._is_logged_in = False

    def login(self):
        """Authenticates with Lufa Farms."""
        try:
            logger.info(f"Navigating to {LOGIN_URL}...")
            response = self.session.get(LOGIN_URL)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            payload = {}
            for input_tag in soup.find_all('input', type='hidden'):
                if input_tag.get('name'):
                    payload[input_tag.get('name')] = input_tag.get('value', '')
            
            # Form fields
            payload['LoginForm[user_email]'] = self.email
            payload['LoginForm[password]'] = self.password
            
            logger.info("Attempting login...")
            post_response = self.session.post(LOGIN_URL, data=payload)
            post_response.raise_for_status()
            
            if "Connexion" not in post_response.text or "Mon compte" in post_response.text:
                 logger.info("Login successful!")
                 self._is_logged_in = True
                 return True
            else:
                 logger.error("Login failed. Check credentials.")
                 return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def get_current_order_id(self):
        """Fetches the current active order ID."""
        if not self._is_logged_in:
            if not self.login():
                return None

        try:
            # We must set XHR header for this internal API
            self.session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
            
            response = self.session.get(API_URL_ORDER_DETAILS)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success') and data.get('orderId'):
                return data['orderId']
            
            logger.warning(f"No active order ID found in response: {data.keys()}")
            return None

        except Exception as e:
            logger.error(f"Error fetching order ID: {e}")
            return None

    def get_order_details(self, order_id):
        """Fetches tracking details for a specific order ID."""
        if not self._is_logged_in:
            if not self.login():
                return None
                
        try:
            self.session.headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            })
            
            data = {'order_id': order_id}
            response = self.session.post(API_URL_TRACK_ORDER, data=data)
            response.raise_for_status()
            
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching order details: {e}")
            return None
