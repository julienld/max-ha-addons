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
        return self._make_request_with_retry("GET", API_URL_ORDER_DETAILS, self._parse_order_id)

    def get_order_details(self, order_id):
        """Fetches tracking details for a specific order ID."""
        data = {'order_id': order_id}
        # Update headers for this specific post
        extra_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        return self._make_request_with_retry("POST", API_URL_TRACK_ORDER, lambda r: r.json(), data=data, headers=extra_headers)

    def _parse_order_id(self, response):
        data = response.json()
        if data.get('success') and data.get('orderId'):
            return data['orderId']
        return None

    def _make_request_with_retry(self, method, url, callback, data=None, headers=None, retry=True):
        """Helper to make a request and retry login if it fails."""
        if not self._is_logged_in:
            if not self.login():
                return None
        
        # Apply extra headers if present
        if headers:
            self.session.headers.update(headers)

        try:
            if method == "GET":
                response = self.session.get(url)
            else:
                response = self.session.post(url, data=data)
            
            response.raise_for_status()
            
            # Check if response implies we are logged out (e.g. redirect to login or invalid JSON)
            # Lufa often redirects to login page which returns 200 OK but is HTML, not JSON
            try:
                result = callback(response)
                # If callback returns None, it might mean logic failed (e.g. success: false), 
                # but not necessarily that we are logged out. 
                # However, for simplicity, if we fail to get expected data, we can try re-logging once.
                if result is None and retry:
                     raise ValueError("Possible session expiration (data invalid).")
                return result
            except (json.JSONDecodeError, ValueError):
                # If we catch a JSON error, it's almost certainly because we got an HTML login page back
                if retry:
                    logger.warning("Session Expired: Authentication token invalid. Logging in again...")
                    self._is_logged_in = False
                    if self.login():
                        return self._make_request_with_retry(method, url, callback, data, headers, retry=False)
                    else:
                        logger.error("Re-login failed.")
                        return None
                else:
                    logger.error("Request failed after re-login attempt.")
                    return None

        except Exception as e:
            logger.error(f"Request error ({url}): {e}")
            if retry:
                 logger.info("Retrying request after error...")
                 return self._make_request_with_retry(method, url, callback, data, headers, retry=False)
            return None
