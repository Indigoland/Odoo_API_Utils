import requests
import json

from .Authenticate import authenticate,odoo_db,odoo_password,odoo_url


# Function to fetch order lines based on sales order IDs
def fetch_order_lines_for_order(order_id):
    user_id = authenticate()
    if user_id is None:
        return

    # Construct the payload to fetch order lines for a specific sale order
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
                "sale.order.line",  # Model to fetch order lines
                "search_read",  # Method to read data
                [
                    [('order_id', '=', order_id),('x_product_tag_ids','not in',[11,12,13])],  # Domain to fetch order lines for the given sale order ID                                                                          # Exclude the 'Service','System' and 'Other' product tags 
                    ["id", "product_id", "product_uom_qty", "is_refurbished", "serial_number"]
                ],
                {   
                    "limit": None,  # Fetch all order lines for this order
                    "order": "price_unit desc"  # Optional: Sort by order line ID
                }
            ],
        },
        "id": None
    }

    try:
        # Make the request to fetch order lines
        response = requests.post(f'{odoo_url}', json=fetch_payload)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            print(f"Error fetching order lines for sale order {order_id}:")
            print(json.dumps(data['error'], indent=2))
        else:
            return data['result']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching order lines for sale order {order_id}: {e}")
        return None