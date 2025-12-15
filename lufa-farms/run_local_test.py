import requests
from bs4 import BeautifulSoup
import getpass
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://montreal.lufa.com"
LOGIN_URL = f"{BASE_URL}/fr/login"

def login(email, password):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    })

    try:
        # Step 1: Get the login page to extract any CSRF tokens
        logger.info(f"Navigating to {LOGIN_URL}...")
        response = session.get(LOGIN_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the form fields
        # Based on research: input IDs are LoginForm_user_email and LoginForm_password
        # We need the 'name' attributes for the POST request
        
        payload = {}
        
        # Find all hidden inputs (often used for CSRF)
        for input_tag in soup.find_all('input', type='hidden'):
            if input_tag.get('name'):
                payload[input_tag.get('name')] = input_tag.get('value', '')
        
        # Add credentials
        # Inspecting the page source usually reveals the name. 
        # Common convention for ID 'LoginForm_user_email' is name='LoginForm[user_email]'
        # We will try to find the inputs by ID to get their proper names
        
        email_input = soup.find('input', id='LoginForm_user_email')
        password_input = soup.find('input', id='LoginForm_password')
        
        if email_input and email_input.get('name'):
            payload[email_input.get('name')] = email
        else:
            logger.warning("Could not find email input element by ID, guessing name 'LoginForm[user_email]'")
            payload['LoginForm[user_email]'] = email
            
        if password_input and password_input.get('name'):
            payload[password_input.get('name')] = password
        else:
            logger.warning("Could not find password input element by ID, guessing name 'LoginForm[password]'")
            payload['LoginForm[password]'] = password
            
        logger.info("Attempting login...")
        post_response = session.post(LOGIN_URL, data=payload)
        post_response.raise_for_status()
        
        # Check if login was successful
        # Using a simple check: if we are redirected to home or dashboard, or if "Connexion" is no longer present
        if "Connexion" not in post_response.text or "Mon compte" in post_response.text:
             logger.info("Login appears successful!")
             return session
        else:
             logger.error("Login failed. Check credentials or form structure.")
             # Debug: print logic to help diagnosis
             # with open("login_fail.html", "w") as f:
             #     f.write(post_response.text)
             return None

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

def main():
    print("Lufa Farms Login Tester")
    print("-----------------------")
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    order_id = input("Order ID (e.g. 24557262): ")
    if not order_id:
        order_id = "24557262"
    
    session = login(email, password)
    
    if session:
        print(f"\nLogin successful! Session established.")
        
        # Step 2: Try to find the current Order ID automatically if not provided
        # or if we want to confirm the logic.
        curr_order_id = order_id
        if not curr_order_id: # If empty, try to fetch via API
             print("Attempting to find current order ID from dashboard...")
        if not curr_order_id or curr_order_id == "24557262": # If default/empty, try to fetch via API
             print("Attempting to find current order ID via API (GetUserOrderDetails)...")
             try:
                 # The user discovered this endpoint which returns JSON with the orderId
                 # URL: https://montreal.lufa.com/fr/superMarket/GetUserOrderDetails
                 # Method: GET
                 file_url = f"{BASE_URL}/fr/superMarket/GetUserOrderDetails"
                 
                 # Ensure we have the right headers for an XHR request if needed, though GET might be simpler
                 session.headers.update({
                     'X-Requested-With': 'XMLHttpRequest'
                 })

                 resp = session.get(file_url)
                 resp.raise_for_status()
                 
                 data = resp.json()
                 if data.get('success') and data.get('orderId'):
                     curr_order_id = data['orderId']
                     print(f"Found active Order ID: {curr_order_id}")
                 else:
                     logger.warning(f"Could not find 'orderId' in API response: {data.keys()}")
                     print("Could not find active order ID from API. Using provided/default ID.")

             except Exception as e:
                 logger.error(f"Failed to fetch order ID from API: {e}")

        # Step 3: Call the internal API
        print(f"Fetching details for Order ID: {curr_order_id}...")
        api_url = f"{BASE_URL}/fr/orders/getTrackOrderData"
        data = {'order_id': curr_order_id}
        
        try:
             # The headers from the user trace show typical browser headers
             # The most important usually are Content-Type and X-Requested-With
             session.headers.update({
                 'X-Requested-With': 'XMLHttpRequest',
                 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
             })
             
             api_resp = session.post(api_url, data=data)
             api_resp.raise_for_status()
             
             try:
                 json_data = api_resp.json()
                 print("\n--- API Response Data ---")
                 print(json.dumps(json_data, indent=2, ensure_ascii=False))
                 
                 # Analyze for entities
                 print("\n--- Potential Entities ---")
                 print(f"Status: {json_data.get('status')}")
                 print(f"ETA: {json_data.get('eta')}")
                 print(f"Stops Before: {json_data.get('stops_before')}")
                 
             except json.JSONDecodeError:
                 print("Response was not JSON. Printing first 500 chars:")
                 print(api_resp.text[:500])
                 
        except Exception as e:
            logger.error(f"API request failed: {e}")
            
    else:
        print("\nLogin failed.")

if __name__ == "__main__":
    main()
