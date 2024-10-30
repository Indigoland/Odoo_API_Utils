import requests
import json

from .Authenticate import authenticate,odoo_db,odoo_password,odoo_url
from .Order_Lines import fetch_order_lines_for_order



# Function to fetch sales orders (with order line IDs) from 'sale.order' model
def fetch_sales_orders():
    user_id = authenticate()
    if user_id is None:
        return

    # Construct the payload to fetch the latest 10 sales orders (from 'sale.order' model)
    fetch_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                odoo_db,  # Odoo database name
                user_id,  # Authenticated user ID
                odoo_password,  # User password
                "sale.order",  # Model to interact with (sale orders)
                "search_read",  # Method to call on the model
                [
                    [('state', 'not in', ('draft', 'sent', 'cancel')),('company_id', '=', 1)],  # Domain to exclude certain states and users

                    # Fields to retrieve: 
                    ["id", "name", "partner_id", "user_id", "invoice_status"]
                ],
                {   # Additional options for the search_read method
                    "limit": 1,  # Fetch only 1 records
                    "order": "date_order desc",  # Order by order date in descending order
                }
            ],
        },
        "id": None
    }

    try:
        # Make the request to fetch sales orders
        response = requests.post(f'{odoo_url}', json=fetch_payload)
        response.raise_for_status()
        data = response.json()

        # Check if the response contains an error
        if "error" in data:
            print("Error fetching sales orders:")
            print(json.dumps(data['error'], indent=2))
        else:
            # Fetch the order line details using order ID
            # Loop through each sale operation record and fetch its related order lines
            for order in data['result']:
                sale_order_id = order['id']
                if sale_order_id:
                    print(f"Sale Order: {json.dumps(order, indent=2)}")

                    # Fetch and print the order lines for this sale order
                    order_lines = fetch_order_lines_for_order(sale_order_id)
                    if order_lines:
                        print(f"Order Lines for Sale Order {sale_order_id}:")
                        print(json.dumps(order_lines, indent=2))

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sales orders: {e}")




