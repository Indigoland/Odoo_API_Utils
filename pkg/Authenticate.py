import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Set up Odoo instance details
odoo_url = os.getenv('ODOO_URL')  # Odoo URL with /jsonrpc endpoint
odoo_db  = os.getenv('ODOO_DB')  # Database name
odoo_user = os.getenv('ODOO_USER') # Odoo login email
odoo_password = os.getenv('ODOO_PASSWORD')  # Odoo login password

# Construct the authentication payload
auth_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",  
        "method": "authenticate",  
        "args": [odoo_db, odoo_user, odoo_password, {}]  # Arguments for the method
    },
    "id": None
}

# Authenticate and get the user ID
def authenticate():
    try:
        response = requests.post(odoo_url, json=auth_payload)
        response.raise_for_status()
        data = response.json()

        # Print the response for debugging
        # print("Response from Odoo:", json.dumps(data, indent=2))

        if 'result' in data:
            user_id = data['result']  # The result contains the user ID
            # print(f"Successfully authenticated. User ID: {user_id}")
            return user_id
        else:
            print("Authentication failed. No 'result' key in the response.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during authentication: {e}")
        return None