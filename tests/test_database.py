import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import DatabaseManager
from models import Customers, Orders, Items
from logger_config import logger


def setup_test_db():
    test_path = Path("data/test_tinydb.json")
    if test_path.exists():
        test_path.unlink()
        print("Старая тестовая БД удалена")
    
    db = DatabaseManager("data/test_tinydb.json")
    return db


def clear_test_db(db):
    db.customers_table.truncate()
    db.orders_table.truncate()
    print("Тестовая БД очищена")


def test_add_customer(db):
    print("\n" + "-"*50)
    print("1. ТЕСТ: Добавление клиента")
    
    customer = Customers(1, "Иван Петров", "+7-123-456-78-90", "Москва, ул. Примерная, д. 1")
    result = db.add_customer(customer)
    
    assert result is not None, "Ошибка: клиент не добавлен"
    assert db.get_customer(1) is not None, "Ошибка: клиент не найден"
    
    print(f"Клиент добавлен: ID={customer.id}, Имя={customer.name}")
    return True


def test_get_customer(db):
    print("\n" + "-"*50)
    print("2. ТЕСТ: Получение клиента")
    
    customer = db.get_customer(1)
    assert customer is not None, "Ошибка: клиент не найден"
    assert customer.name == "Иван Петров", f"Ошибка: имя {customer.name} != Иван Петров"
    assert customer.phone == "+7-123-456-78-90", f"Ошибка: телефон {customer.phone}"
    
    print(f"Клиент найден: {customer.name}, {customer.phone}, {customer.address}")
    return True


def test_update_customer(db):
    print("\n" + "-"*50)
    print("3. ТЕСТ: Обновление клиента")
    
    customer = db.get_customer(1)
    customer.name = "Иван Сидоров"
    customer.phone = "+7-987-654-32-10"
    customer.address = "СПб, Невский пр., д. 10"
    
    result = db.update_customer(customer)
    assert result is True, "Ошибка: клиент не обновлен"
    
    updated = db.get_customer(1)
    assert updated.name == "Иван Сидоров", f"Ошибка: имя {updated.name}"
    assert updated.phone == "+7-987-654-32-10", f"Ошибка: телефон {updated.phone}"
    
    print(f"Клиент обновлен: {updated.name}, {updated.phone}, {updated.address}")
    return True


def test_get_all_customers(db):
    print("\n" + "-"*50)
    print("4. ТЕСТ: Получение всех клиентов")
    
    customer2 = Customers(2, "Петр Иванов", "+7-111-222-33-44", "Казань, ул. Центральная, д. 5")
    db.add_customer(customer2)
    
    customers = db.get_all_customers()
    assert len(customers) == 2, f"Ошибка: {len(customers)} != 2"
    
    print(f"Всего клиентов: {len(customers)}")
    for c in customers:
        print(f"   - {c.id}: {c.name}")
    return True


def test_delete_customer_without_orders(db):
    print("\n" + "-"*50)
    print("5. ТЕСТ: Удаление клиента без заказов")
    
    result = db.delete_customer(2)
    assert result is True, "Ошибка: клиент не удален"
    
    customers = db.get_all_customers()
    assert len(customers) == 1, f"Ошибка: {len(customers)} != 1"
    
    print(f"Клиент ID=2 удален")
    return True


def test_add_order(db):
    
    print("\n" + "-"*50)
    print("6. ТЕСТ: Добавление заказа")
    
    if not db.get_customer(1):
        print("   Создаю клиента для заказа...")
        customer = Customers(1, "Иван", "+7-123-456-78-90", "Москва")
        db.add_customer(customer)
    
    items = [
        Items("Пицца", 2, 750), 
        Items("Кока-Кола", 1, 150)
    ]
    
    if db.get_order(1):
        print("   Заказ ID 1 уже существует, удаляю...")
        db.delete_order(1)
    
    order = Orders(1, 1, "2025-04-20", "новый", items)
    result = db.add_order(order)
    
    assert result is not None, "Ошибка: заказ не добавлен"
    assert db.get_order(1) is not None, "Ошибка: заказ не найден"
    
    print(f"Заказ добавлен: ID={order.id}, сумма={order.total} руб., товаров={len(order.items)}")
    for item in items:
        print(f"   - {item.product_name}: {item.quantity} x {item.price} = {item.total} руб.")
    return True

def test_get_order(db):
    print("\n" + "-"*50)
    print("7. ТЕСТ: Получение заказа")
    
    order = db.get_order(1)
    assert order is not None, "Ошибка: заказ не найден"
    assert order.status == "новый", f"Ошибка: статус {order.status}"
    assert order.total == 1650.0, f"Ошибка: сумма {order.total} != 1650"
    assert len(order.items) == 2, f"Ошибка: товаров {len(order.items)} != 2"
    
    print(f"Заказ найден: ID={order.id}, статус={order.status}, сумма={order.total} руб.")
    for item in order.items:
        print(f"   - {item.product_name}: {item.quantity} x {item.price} = {item.total} руб.")
    return True


def test_update_order_status(db):
    print("\n" + "-"*50)
    print("8. ТЕСТ: Обновление статуса заказа")
    result = db.update_order_status(1, "выполнен") 
    assert result is True, "Ошибка: статус не обновлен"
    
    order = db.get_order(1)
    assert order.status == "выполнен", f"Ошибка: статус {order.status} != выполнен"  
    
    print(f"Статус заказа ID=1 изменен на 'выполнен'")
    return True


def test_get_orders_by_customer(db):
    print("\n" + "-"*50)
    print("9. ТЕСТ: Получение заказов клиента")
    
    orders = db.get_orders_by_customer(1)
    assert len(orders) == 1, f"Ошибка: {len(orders)} != 1"
    
    print(f"У клиента ID=1 найдено заказов: {len(orders)}")
    return True


def test_get_customer_total_spent(db):
    print("\n" + "-"*50)
    print("10. ТЕСТ: Сумма трат клиента")
    
    total = db.get_customer_total_spent(1)
    assert total == 1650.0, f"Ошибка: сумма {total} != 1650"
    
    print(f"Клиент ID=1 потратил: {total} руб.")
    return True


def test_search_orders_by_product(db):
    print("\n" + "-"*50)
    print("11. ТЕСТ: Поиск заказов по товару")
    
    orders = db.search_orders_by_product("Пицца")
    assert len(orders) == 1, f"Ошибка: найдено {len(orders)} заказов"
    
    print(f"Найдено заказов с 'Пицца': {len(orders)}")
    return True


def test_delete_customer_with_orders(db):
    print("\n" + "-"*50)
    print("12. ТЕСТ: Удаление клиента с заказами (отказ)")
    
    result = db.delete_customer(1)
    assert result is False, "Ошибка: клиент с заказами был удален"
    
    print(f"Клиент с заказами НЕ удален (защита сработала)")
    return True


def test_delete_order(db):
    print("\n" + "-"*50)
    print("13. ТЕСТ: Удаление заказа")
    
    result = db.delete_order(1)
    assert result is True, "Ошибка: заказ не удален"
    
    order = db.get_order(1)
    assert order is None, "Ошибка: заказ все еще существует"
    
    print(f"Заказ ID=1 удален")
    return True


def test_delete_customer_after_orders(db):
    print("\n" + "-"*50)
    print("14. ТЕСТ: Удаление клиента после удаления заказов")
    
    result = db.delete_customer(1)
    assert result is True, "Ошибка: клиент не удален"
    
    customer = db.get_customer(1)
    assert customer is None, "Ошибка: клиент все еще существует"
    
    print(f"Клиент ID=1 удален (после удаления заказов)")
    return True

def test_close(db):
    print("\n" + "-"*50)
    print("15. ТЕСТ: Закрытие БД")
    
    db.close()
    print(f"Соединение с БД закрыто")
    return True


def run_all_tests():
    db = None
    passed = 0
    failed = 0
    tests = [
        ("Добавление клиента", test_add_customer),
        ("Получение клиента", test_get_customer),
        ("Обновление клиента", test_update_customer),
        ("Получение всех клиентов", test_get_all_customers),
        ("Удаление клиента без заказов", test_delete_customer_without_orders),
        ("Добавление заказа", test_add_order),
        ("Получение заказа", test_get_order),
        ("Обновление статуса", test_update_order_status),
        ("Заказы по клиенту", test_get_orders_by_customer),
        ("Сумма трат клиента", test_get_customer_total_spent),
        ("Поиск по товару", test_search_orders_by_product),
        ("Удаление клиента с заказами", test_delete_customer_with_orders),
        ("Удаление заказа", test_delete_order),
        ("Удаление клиента после заказов", test_delete_customer_after_orders),
    ]
    
    try:
        db = setup_test_db()
        
        for name, test_func in tests:
            try:
                test_func(db)
                passed += 1
            except AssertionError as e:
                failed += 1
                print(f"{name}: {e}")
            except Exception as e:
                failed += 1
                print(f"{name}: Ошибка - {e}")
    
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
    
    finally:
        if db:
            test_close(db)
    
    print("\n" + "-"*60)
    print("РЕЗУЛЬТАТЫ")
    print(f"Пройдено: {passed}")
    print(f"Не пройдено: {failed}")
    print(f"Всего: {passed + failed}")
    
    
    if failed == 0:
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(f"Есть ошибки! Пройдено {passed} из {passed + failed}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)