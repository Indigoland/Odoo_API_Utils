import requests
import json

from .Authenticate import authenticate,odoo_db,odoo_password,odoo_url
from .Firebase_Utils import initialize_firebase, push_to_firebase

product_tag_mapping = {
1: 'Zone C',
2: 'Zone A',
3: 'Zone F',
4: 'Zone E',
5: 'Zone D',
6: 'Cave',
7: 'Device',
8: 'For Import',
9: 'Accessories',
10: 'so the easiest/most efficient way',
11: 'Service',
12: 'Other',
13: 'System',
14: 'Component'
}


# Function to fetch the product list (from 'product.product' model)
def fetch_product_list(verbose=False):
    user_id = authenticate()
    if user_id is None:
        return

    # Construct the payload to fetch the product list
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
                "product.product",  # Model to interact with
                "search_read",  # Method 
                [
                    [("product_tag_ids","in",(7))],                   # Fetch product which has 'Device' tag  
                    ["id", "default_code", "name","product_tag_ids"]  # Fields to retrieve 
                ],
                { 
                    "limit": None,  # Limit the number of results
                    "order": "name asc"  # Order by product name 
                }
            ],
        },
        "id": None
    }

    try:
        # Make the request to fetch the product list
        response = requests.post(f'{odoo_url}', json=fetch_payload)
        response.raise_for_status()
        data = response.json()

        # Check if the response contains an error
        if "error" in data:
            print("Error fetching product list:")
            print(json.dumps(data['error'], indent=2))
            return []

        # Print the product list if verbose is set to True
        if verbose:
            print("Product List Fetched:")
            print(json.dumps(data['result'], indent=2))

        return data['result']  

    except requests.exceptions.RequestException as e:
        print(f"Error fetching product list: {e}")
        return []



def firebase_upload_product_list():
    
    initialize_firebase()

    print('Fetching from odoo product lists..')
    product_list = fetch_product_list()

    cleaned_product_list = []

    for product in product_list:

        product_tag_ids = product.get('product_tag_ids',[])  # Defaults to empty list if None
        product_tag_names = [product_tag_mapping.get(product_tag_id,'Unknown') for product_tag_id in product_tag_ids]

        cleaned_product = {
            'id': product.get('id'),
            'internal_reference': product.get('default_code',''),
            'name': product.get('name'),
            'product_tag': product_tag_names
        }

        cleaned_product_list.append(cleaned_product)


        product_id = cleaned_product.get('id')
        push_to_firebase('devices_list',str(product_id),cleaned_product)

    print('Update completed')



    