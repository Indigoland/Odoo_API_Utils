import requests
import json

from .Authenticate import authenticate, odoo_db, odoo_password, odoo_url

# Function to fetch customer information from the 'res.partner' model
def fetch_customers(verbose=False):
    user_id = authenticate()
    if user_id is None:
        print("Authentication failed.")
        return []

    # Construct the payload to fetch customer data
    fetch_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                odoo_db,
                user_id,
                odoo_password,
                "res.partner",  # Model to interact with
                "search_read",  # Method
                [
                    [("name", "in", ("",))],  # Domain filter
                    ["id", "name", "is_company", "category_id","commercial_partner_id","parent_id"]  # Fields to retrieve
                ],
                {
                    "limit": None,  # Limit the number of results
                    "order": "name asc"  # Order by customer name
                }
            ],
        },
        "id": None
    }

    try:
        # Make the request to fetch customer information
        response = requests.post(f'{odoo_url}', json=fetch_payload)
        response.raise_for_status()
        data = response.json()

        # Check if the response contains an error
        if "error" in data:
            print("Error fetching customer information:")
            print(json.dumps(data['error'], indent=2))
            return []

        # Print the customer list if verbose is set to True
        if verbose:
            print("Customer List Fetched:")
            print(json.dumps(data['result'], indent=2))

        return data['result']  

    except requests.exceptions.RequestException as e:
        print(f"Error fetching customer information: {e}")
        return []
