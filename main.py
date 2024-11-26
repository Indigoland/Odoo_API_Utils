from pkg.Sales_Op import fetch_sale_operation_panel, clean_and_combine_sale_operation_panel, firebase_upload_sale_operation_panel
from pkg.Sales_Orders import fetch_sales_orders
from pkg.Authenticate import authenticate
from pkg.Product import fetch_product_list, firebase_upload_product_list
from pkg.Firebase_Utils import initialize_firebase,push_to_firebase
from pkg.completed.Inventory_Status import update_products_sale_ok_true_to_rent_ok_true
from pkg.completed.Product_Tag import update_products_tags_from_excel
from pkg.Customer import fetch_customers
from pkg.Invoice import fetch_invoices, update_commercial_partner_for_invoices



if __name__ == "__main__":
    #fetch_sales_orders()
    #fetch_product_list(True)
    #firebase_upload_product_list()
    #fetch_sale_operation_panel()
    #clean_and_combine_sale_operation_panel()
    firebase_upload_sale_operation_panel()
    #update_products_tags_from_excel()
    #update_products_sale_ok_true_to_rent_ok_true()
    #fetch_customers(True)
    #fetch_invoices(True)
    #update_commercial_partner_for_invoices(43513,18174)

   
  
    



