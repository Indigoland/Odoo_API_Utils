
# Mapping dictionary for couriers
delivery_type_mapping = {
    1: 'DHL',
    2: 'Link Logistics',
    3: 'FedEx',
    4: 'Zendr'
}

# Mapping dictionary for operation status
status_ops_mapping = {
    1: 'Hold',
    2: 'Approved',
    3: 'Released',
    4: 'Awaiting Payment',
    5: 'Awaiting Inventory',
    6: 'Canceled',
    7: 'Shipped from ENA',
    8: 'Under Foiling',
    9: 'Delayed Shipping',
    10: 'Payment Received'
}


# Function to clean and flatten sale order data
def clean_sale_order_data(raw_sale_order_data):
    cleaned_data = []
    
    for order in raw_sale_order_data:

        # Flatten fields (assuming it's a list [id, name])
        sale_order_id = order.get('sale_order_id', [None, None])[1]
        stage_id = order.get('stage_id',[None,None])[1]
        order_type_id = order.get('order_type_id',[None,None])[1]
        packing_letter = order.get('packing_letter',[])

        # Transform delivery_type_ids from numbers to courier names
        status_ops_ids = order.get('status_ops_ids',[])
        status_ops_names = [status_ops_mapping.get(status_ops_id, 'Unknown') for status_ops_id in status_ops_ids]

        # Transform stage_ops_ids from numbers to names
        delivery_type_ids = order.get('delivery_type_ids', [])
        courier_names = [delivery_type_mapping.get(delivery_type_id, 'Unknown') for delivery_type_id in delivery_type_ids]
        
        # Remove redundant fields and structure the data
        cleaned_order = {
            'sale_order_id': sale_order_id,
            'order_type_id': order_type_id,
            'stage_id': stage_id,
            'status_ops_names': status_ops_names,
            'packing_letter': packing_letter,
            'courier_names': courier_names
        }
        cleaned_data.append(cleaned_order)
    
    return cleaned_data


# Function to clean and flatten order line data
def clean_order_line_data(raw_order_line_data):
    cleaned_data = []
    
    for line in raw_order_line_data:

        product_id_original = line.get('product_id')

        # Skip lines where product_id is False (Usually line dividers in order lines)
        if not product_id_original:
            continue

        # Flatten product_id for a list [id, name]
        product_id = product_id_original[0]
        product_name = product_id_original[1]

        # Remove redundant fields and structure the data
        cleaned_line = {
            'product_id': product_id,
            'product_name': product_name,
            'quantity': line.get('product_uom_qty'),
            'is_refurbished': line.get('is_refurbished'),
            'serial_number': line.get('serial_number')
        }
        cleaned_data.append(cleaned_line)
    
    return cleaned_data     
