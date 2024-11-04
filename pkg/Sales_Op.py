import requests
import json
from .Authenticate import authenticate, odoo_db, odoo_password, odoo_url
from .Order_Lines import fetch_order_lines_for_order
from .Data_Cleaning import clean_sale_order_data
from .Data_Cleaning import clean_order_line_data
from .Firebase_Utils import initialize_firebase, push_to_firebase,fetch_existing_firebase_ids, delete_firebase_documents

# Fetch weekly shipping orders from 'sale.operation.panel' and print each order with its order lines
def fetch_sale_operation_panel():
    user_id = authenticate()
    if user_id is None:
        return

    # Construct the payload to fetch records from 'sale.operation.panel' model
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
                "sale.operation.panel",  # Model to interact with (sale operation panel)
                "search_read",  # Method to call on the model
                [
                    [('stage_id', 'in', ('Monday', 'Tuesday','Wednesday','Thursday','Friday'))],  # Domain filter 
                    #[('sale_order_id', 'in', ('S03510'))],
                    ["id", "sale_order_id","order_type_id","stage_id", "status_ops_ids","packing_letter","delivery_type_ids"]  # Fields to retrieve
                ],
                {   
                    "limit": None,  
                    "order": "write_date desc"  # Order by write date
                }
            ],
        },
        "id": None
    }

    try:
        # Make the request to fetch details from 'sale.operation.panel'
        response = requests.post(f'{odoo_url}', json=fetch_payload)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            print("Error fetching sale operation panel records:")
            print(json.dumps(data['error'], indent=2))
        else:
            print("Sale Operation Panel records fetched.")

            # Loop through each sale operation record and fetch its related order lines
            for order in data['result']:
                sale_order_id = order['sale_order_id'][0] 

                if sale_order_id:
                    # print(f"Sale Order: {json.dumps(order, indent=2)}")

                    # Fetch and print the order lines for this sale order
                    order_lines = fetch_order_lines_for_order(sale_order_id)
                    if order_lines:
                        # print(f"Order Lines for Sale Order {sale_order_id}:")
                        # print(json.dumps(order_lines, indent=2))
                        pass

            print("Order lines all fetched.")

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sale operation panel records: {e}")


 
def clean_and_combine_sale_operation_panel():
    user_id = authenticate()
    if user_id is None:
        return

    # Fetch raw sale orders from 'sale.operation.panel'
    raw_orders_response = fetch_sale_operation_panel()

    # Extract the 'result' from the raw response
    raw_sale_orders = raw_orders_response.get('result', [])

    if raw_sale_orders:
        # Clean the sale order data
        cleaned_sale_orders = clean_sale_order_data(raw_sale_orders)
        combined_orders = []

        for order in cleaned_sale_orders:
            
            # Fetch raw order lines for each sale order
            raw_order_lines = fetch_order_lines_for_order(order['sale_order_id'])

            if raw_order_lines:
                cleaned_order_lines = clean_order_line_data(raw_order_lines)
                
                # Combine sale order and order lines
                combined_order = {
                    "order_lines": cleaned_order_lines, 
                    "courier_names": order.get('courier_names', []), 
                    "packing_letter": order.get('packing_letter', []), 
                    "status_ops_names": order.get('status_ops_names', []),  
                    "stage_id": order.get('stage_id', ''), 
                    "order_type_id": order.get('order_type_id',''),
                    "sale_order_id": order['sale_order_id']                   
                }

                # Add the combined order to the list
                combined_orders.append(combined_order)

        print("Sale Orders and Order Lines are cleaned and combined.")
        return combined_orders
    



# Main function to upload and synchronize data with Firebase
def firebase_upload_sale_operation_panel():
    # Initialize Firebase
    initialize_firebase()

    # Fetch and clean data from Odoo
    print("Fetching and cleaning sale operation data from Odoo...")
    cleaned_data = clean_and_combine_sale_operation_panel()

    # Retrieve all current order IDs in Firebase
    print("Fetching existing orders from Firebase...")
    existing_orders = fetch_existing_firebase_ids('weeklyorders_odoo')
    existing_order_ids = set(existing_orders.keys())
    
    # Extract new order IDs from cleaned data
    new_order_data = {str(order.get('sale_order_id')): order for order in cleaned_data}
    new_order_ids = set(new_order_data.keys())
    
    # Determine orders to delete, update, and create
    to_delete = existing_order_ids - new_order_ids
    to_update = existing_order_ids & new_order_ids
    to_create = new_order_ids - existing_order_ids

    # Update existing orders in Firebase with new data
    if to_update:
        for order_id in to_update:
            existing_data = existing_orders[order_id]
        
            # Only update the fields present in new_order_data without overwriting others
            merged_data = {**existing_data, **new_order_data[order_id]}
        
            push_to_firebase('weeklyorders_odoo', order_id, merged_data)
            print(f"Order {order_id} updated in Firebase.")
    else:
        print("No orders need to be updated.")

    
    # Create new orders in Firebase that do not exist in the collection
    if to_create:
        for order_id in to_create:
            push_to_firebase('weeklyorders_odoo', order_id, new_order_data[order_id])
            print(f"Order {order_id} created in Firebase.")
    else:
        print("No new orders need to be created.")

    # Delete orders that are no longer in the new data
    if to_delete:
        delete_firebase_documents('weeklyorders_odoo', to_delete)
    else:
        print("No orders need to be deleted.")
        

    print("Firebase synchronization complete.")


                



