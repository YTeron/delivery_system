from typing import List, Optional
from pathlib import Path
from tinydb import TinyDB, Query
import json
from models import Customers, Orders, Items
from logger_config import logger


class DatabaseManager:
    
    def __init__(self, db_path: str = "data/tinydb.json"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        if not Path(db_path).exists():
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        
        self.db = TinyDB(db_path)
        self.customers_table = self.db.table('customers')
        self.orders_table = self.db.table('orders')
        self.query = Query()
    
    # ------------------------------------------------------
    
    def add_customer(self, customer: Customers) -> int:
        logger.info(f"Добавление клиента: {customer.name}")
        customer_dict = {
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "address": customer.address
        }
        return self.customers_table.insert(customer_dict)
    
    def get_customer(self, customer_id: int) -> Optional[Customers]:
        result = self.customers_table.get(self.query.id == customer_id)
        if result:
            return Customers(
                id=result["id"],
                name=result["name"],
                phone=result["phone"],
                address=result["address"]
            )
        return None
    
    def get_all_customers(self) -> List[Customers]:
        customers = []
        for data in self.customers_table.all():
            customers.append(Customers(
                id=data["id"],
                name=data["name"],
                phone=data["phone"],
                address=data["address"]
            ))
        return customers
    
    def update_customer(self, customer: Customers) -> bool:
        logger.info(f"Обновлён клиент: {customer.name}")
        result = self.customers_table.update(
            {
                "name": customer.name,
                "phone": customer.phone,
                "address": customer.address
            },
            self.query.id == customer.id
        )
        return len(result) > 0
    
    def delete_customer(self, customer_id: int) -> bool:
        customer = self.get_customer(customer_id)
        if not customer:
            logger.warning(f"Попытка удалить несуществующего клиента: ID {customer_id}")
            return False
        
        orders = self.get_orders_by_customer(customer_id)
        if orders:
            logger.warning(f"Нельзя удалить клиента {customer.name} (ID: {customer_id}), у него {len(orders)} заказ(ов)")
            return False
        
        logger.info(f"Удаление клиента: {customer.name} (ID: {customer_id})")
        
        self.orders_table.remove(self.query.customer_id == customer_id)
        
        removed = self.customers_table.remove(self.query.id == customer_id)
        result = len(removed) > 0 
        
        if result:
            logger.info(f"Клиент ID {customer_id} успешно удалён")
        else:
            logger.error(f"Не удалось удалить клиента ID {customer_id}")
    
        return result
    
    def is_customer(self, customer_id: int) -> bool:
        return self.is_customer_exists(customer_id)
    # ------------------------------------------------
    
    def add_order(self, order: Orders) -> int:
        logger.info(f"Добавление заказа: ID {order.id} для клиента ID {order.id_customers}")
        order_dict = {
            "id": order.id,
            "customer_id": order.id_customers,
            "order_date": order.date,
            "status": order.status,
            "total": order.total,
            "items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "price": item.price
                }
                for item in order.items
            ]
        }
        return self.orders_table.insert(order_dict)
    
    def get_order(self, order_id: int) -> Optional[Orders]:
        result = self.orders_table.get(self.query.id == order_id)
        if result:
            items = [
                Items(
                    product_name=item["product_name"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                for item in result["items"]
            ]
            return Orders(
                id=result["id"],
                id_customers=result["customer_id"],
                date=result["order_date"],
                status=result["status"],
                items=items
            )
        return None
    
    def get_all_orders(self) -> List[Orders]:
        orders = []
        for data in self.orders_table.all():
            items = [
                Items(
                    product_name=item["product_name"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                for item in data["items"]
            ]
            orders.append(Orders(
                id=data["id"],
                id_customers=data["customer_id"],
                date=data["order_date"],
                status=data["status"],
                items=items
            ))
        return orders
    
    def get_orders_by_customer(self, customer_id: int) -> List[Orders]:
        results = self.orders_table.search(self.query.customer_id == customer_id)
        orders = []
        for data in results:
            items = [
                Items(
                    product_name=item["product_name"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                for item in data["items"]
            ]
            orders.append(Orders(
                id=data["id"],
                id_customers=data["customer_id"],
                date=data["order_date"],
                status=data["status"],
                items=items
            ))
        return orders
    
    def update_order_status(self, order_id: int, new_status: str) -> bool:
        valid_statuses = ["новый", "в доставке", "выполнен", "отменён"]
        
        if new_status not in valid_statuses:
            logger.error(f"Неверный статус: {new_status}. Допустимые значения: {', '.join(valid_statuses)}")
            return False
        
        order = self.get_order(order_id)
        if order:
            old_status = order.status
            logger.info(f"Изменение статуса заказа ID {order_id}: '{old_status}' -> '{new_status}'")
        else:
            logger.warning(f"Попытка изменить статус несуществующего заказа: ID {order_id}")
            return False
        
        result = self.orders_table.update(
            {"status": new_status},
            self.query.id == order_id
        )
        
        if len(result) > 0:
            logger.info(f"Статус заказа ID {order_id} успешно изменён на '{new_status}'")
            return True
        else:
            logger.error(f"Не удалось изменить статус заказа ID {order_id}")
            return False
    
    def delete_order(self, order_id: int) -> bool:
        order = self.get_order(order_id)
        if not order:
            logger.warning(f"Попытка удалить несуществующий заказ: ID {order_id}")
            return False
        
        logger.info(f"Удаление заказа ID {order_id}")
        removed = self.orders_table.remove(self.query.id == order_id)
        result = len(removed) > 0  # ← ИСПРАВЛЕНО: сравниваем длину списка
        
        if result:
            logger.info(f"Заказ ID {order_id} успешно удалён")
        else:
            logger.error(f"Не удалось удалить заказ ID {order_id}")
        
        return result
    
    def get_orders_by_status(self, status: str) -> List[Orders]:
        results = self.orders_table.search(self.query.status == status)
        orders = []
        for data in results:
            items = [
                Items(
                    product_name=item["product_name"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                for item in data["items"]
            ]
            orders.append(Orders(
                id=data["id"],
                id_customers=data["customer_id"],
                date=data["order_date"],
                status=data["status"],
                items=items
            ))
        return orders
    
    def get_customer_total_spent(self, customer_id: int) -> float:
        orders = self.get_orders_by_customer(customer_id)
        return sum(order.total for order in orders)
    
    def search_orders_by_product(self, product_name: str) -> List[Orders]:
        all_orders = self.get_all_orders()
        return [
            order for order in all_orders
            if any(product_name.lower() in item.product_name.lower() for item in order.items)
        ]
    
    def close(self):
        self.db.close()