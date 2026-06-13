from typing import List
from datetime import datetime

class OrderStatus:
    NEW = "новый"
    DELIVERY = "в доставке"
    COMPLETED = "выполнен"
    CANCELLED = "отменён"
    
    ALL = [NEW, DELIVERY, COMPLETED, CANCELLED]


class Customers:
    def __init__(self, id: int, name: str, phone: str, address: str):
        self.id = id
        self.name = name
        self.phone = phone
        self.address = address


class Orders:
    def __init__(self, id: int, id_customers: int, date: str, status: str, items: List['Items']):
        self.id = id
        self.id_customers = id_customers
        self.date = date
        self.status = self._validate_status(status)
        self.items = items
    
    def _validate_status(self, status: str) -> str:
        if status not in OrderStatus.ALL:
            raise ValueError(f"Неверный статус: {status}. Допустимые значения: {', '.join(OrderStatus.ALL)}")
        return status
    
    @property
    def status(self) -> str:
        return self._status
    
    @status.setter
    def status(self, value: str):
        if value not in OrderStatus.ALL:
            raise ValueError(f"Неверный статус: {value}. Допустимые значения: {', '.join(OrderStatus.ALL)}")
        self._status = value
    
    @property
    def date_obj(self) -> datetime:
        return datetime.strptime(self.date, "%Y-%m-%d")
    
    @date_obj.setter
    def date_obj(self, value: datetime):
        self.date = value.strftime("%Y-%m-%d")
    
    @property
    def total(self) -> float:
        return sum(item.total for item in self.items)


class Items:
    def __init__(self, product_name: str, quantity: int, price: float):
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
    
    @property
    def total(self) -> float:
        return self.quantity * self.price