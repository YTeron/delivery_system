import json
from typing import List
from pathlib import Path
from database import DatabaseManager
from models import Customers, Orders, Items

class DataExporter:
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def export_to_json(self, filepath: str = "data/export.json"):
        customers = self.db.get_all_customers()
        orders = self.db.get_all_orders()
        
        print(f"Экспорт клиентов: {len(customers)}")
        print(f"Экспорт заказов: {len(orders)}")
        
        data = {
            "customers": [
                {
                    "id": c.id,
                    "name": c.name,
                    "phone": c.phone,
                    "address": c.address
                }
                for c in customers
            ],
            "orders": [
                {
                    "id": o.id,
                    "customer_id": o.id_customers,
                    "order_date": o.date,
                    "status": o.status,
                    "total": o.total,
                    "items": [
                        {
                            "product_name": i.product_name,
                            "quantity": i.quantity,
                            "price": i.price
                        }
                        for i in o.items
                    ]
                }
                for o in orders
            ]
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Экспорт завершен: {filepath}")
    
    def import_from_json(self, filepath: str, clear_existing: bool = False):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if clear_existing:
            self.db.customers_table.truncate()
            self.db.orders_table.truncate()
        
        for cust_data in data.get("customers", []):
            if not self.db.get_customer(cust_data["id"]):
                customer = Customers(
                    id=cust_data["id"],
                    name=cust_data["name"],
                    phone=cust_data["phone"],
                    address=cust_data["address"]
                )
                self.db.add_customer(customer)
        
        for order_data in data.get("orders", []):
            if not self.db.get_order(order_data["id"]):
                items = [
                    Items(
                        product_name=item["product_name"],
                        quantity=item["quantity"],
                        price=item["price"]
                    )
                    for item in order_data["items"]
                ]
                order = Orders(
                    id=order_data["id"],
                    id_customers=order_data["customer_id"],
                    date=order_data["order_date"],
                    status=order_data["status"],
                    items=items
                )
                self.db.add_order(order)