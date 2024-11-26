import requests
import json

from .Authenticate import authenticate, odoo_db, odoo_password, odoo_url

# Function to fetch customer information from the 'res.partner' model
def fetch_invoices(verbose=False):
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
                "account.move",  # Model to interact with
                "search_read",  # Method
                [
                    #[("name", "in", ("INV/2023/00293","INV/2024/02006"))],  # Domain filter
                    [('partner_id',"in",("Sport & Health Solutions SPA, Roberto Frazzoni",)),
                     # ("payment_state","=","paid"),
                     ("company_id","=","Exxentric AB")],
                    ["id", "name", "partner_id", "commercial_partner_id"]  # Fields to retrieve
                ],
                {
                    "limit": None,  # Limit the number of results
                    "order": "name desc"  # Order by customer name
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
            print("Error fetching invoice information:")
            print(json.dumps(data['error'], indent=2))
            return []

        # Print the customer list if verbose is set to True
        if verbose:
            print("Invoice List Fetched:")
            print(json.dumps(data['result'], indent=2))

        return data['result']  

    except requests.exceptions.RequestException as e:
        print(f"Error fetching invoice information: {e}")
        return []
    


import requests
from .Authenticate import authenticate, odoo_db, odoo_password, odoo_url

def update_commercial_partner_for_invoices(target_partner_id, new_commercial_partner_id):
    """
    Updates the commercial_partner_id for all invoices associated with a specific partner_id.

    :param target_partner_id: The partner_id to filter invoices (int).
    :param new_commercial_partner_id: The ID of the new commercial partner (int).
    """
    # Authenticate and get the user ID
    user_id = authenticate()
    if user_id is None:
        print("Authentication failed.")
        return

    # Construct the payload to search for invoices with the specific partner_id
    search_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                odoo_db,
                user_id,
                odoo_password,
                "account.move",  # Model to interact with
                "search",  # Method to search
                [[("partner_id", "=", target_partner_id)]],  # Domain filter
            ],
        },
        "id": None
    }

    try:
        # Fetch invoices with the target partner_id
        response = requests.post(odoo_url, json=search_payload)
        response.raise_for_status()
        invoice_ids = response.json().get('result', [])

        if not invoice_ids:
            print(f"No invoices found for partner_id {target_partner_id}.")
            return

        print(f"Found {len(invoice_ids)} invoices for partner_id {target_partner_id}.")

        # Initialize counters for logging
        success_count = 0
        failure_count = 0

        # Update each invoice's commercial_partner_id
        for invoice_id in invoice_ids:
            update_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        odoo_db,
                        user_id,
                        odoo_password,
                        "account.move",  # Model to interact with
                        "write",  # Method to update
                        [
                            [invoice_id],  # IDs of the records to update
                            {"commercial_partner_id": new_commercial_partner_id}  # Fields to update
                        ]
                    ],
                },
                "id": None
            }

            try:
                update_response = requests.post(odoo_url, json=update_payload)
                update_response.raise_for_status()
                update_result = update_response.json()

                if "error" in update_result:
                    print(f"Failed to update invoice {invoice_id}: {update_result['error']}")
                    failure_count += 1
                else:
                    print(f"Successfully updated invoice {invoice_id}.")
                    success_count += 1

            except requests.exceptions.RequestException as e:
                print(f"Error updating invoice {invoice_id}: {e}")
                failure_count += 1

        # Log summary
        print(f"Update completed. Success: {success_count}, Failures: {failure_count}.")

    except requests.exceptions.RequestException as e:
        print(f"Error searching for invoices: {e}")

