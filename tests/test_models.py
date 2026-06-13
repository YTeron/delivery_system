import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Customers, Orders, Items
from datetime import datetime


def test_customer_creation():
    print("\n" + "-"*50)
    print("1. ТЕСТ: Создание клиента")

    customer = Customers(1, "Иван Петров", "+7-123-456-78-90", "Москва, ул. Примерная, д. 1")
    
    assert customer.id == 1, f"Ошибка: id={customer.id}"
    assert customer.name == "Иван Петров", f"Ошибка: name={customer.name}"
    assert customer.phone == "+7-123-456-78-90", f"Ошибка: phone={customer.phone}"
    assert customer.address == "Москва, ул. Примерная, д. 1", f"Ошибка: address={customer.address}"
    
    print(f"Клиент создан: {customer.id} | {customer.name} | {customer.phone} | {customer.address}")
    return True


def test_customer_update():
    print("\n" + "-"*50)
    print("2. ТЕСТ: Обновление атрибутов клиента")
    
    customer = Customers(1, "Иван", "+7-123-456-78-90", "Москва")
    customer.name = "Иван Сидоров"
    customer.phone = "+7-987-654-32-10"
    customer.address = "СПб, Невский пр., д. 10"
    
    assert customer.name == "Иван Сидоров", f"Ошибка: name={customer.name}"
    assert customer.phone == "+7-987-654-32-10", f"Ошибка: phone={customer.phone}"
    assert customer.address == "СПб, Невский пр., д. 10", f"Ошибка: address={customer.address}"
    
    print(f"Клиент обновлен: {customer.name} | {customer.phone} | {customer.address}")
    return True


def test_item_creation():
    print("\n" + "-"*50)
    print("3. ТЕСТ: Создание товара")
    
    item = Items("Пицца Маргарита", 2, 750)
    
    assert item.product_name == "Пицца Маргарита", f"Ошибка: product_name={item.product_name}"
    assert item.quantity == 2, f"Ошибка: quantity={item.quantity}"
    assert item.price == 750, f"Ошибка: price={item.price}"
    
    print(f"Товар создан: {item.product_name} | {item.quantity} x {item.price} = {item.total} руб.")
    return True


def test_item_total():
    print("\n" + "-"*50)
    print("4. ТЕСТ: Вычисление total товара")
    
    item1 = Items("Пицца", 2, 750)
    assert item1.total == 1500, f"Ошибка: total={item1.total} (должно быть 1500)"
    
    item2 = Items("Кола", 3, 100)
    assert item2.total == 300, f"Ошибка: total={item2.total} (должно быть 300)"
    
    item3 = Items("Чай", 1, 50)
    assert item3.total == 50, f"Ошибка: total={item3.total} (должно быть 50)"
    
    print(f"total работает: Пицца (2x750={item1.total}), Кола (3x100={item2.total}), Чай (1x50={item3.total})")
    return True


def test_order_creation():
    print("\n" + "-"*50)
    print("5. ТЕСТ: Создание заказа")
    
    items = [
        Items("Пицца Маргарита", 2, 750),
        Items("Кока-Кола", 1, 150)
    ]
    
    order = Orders(1, 1, "2025-04-20", "новый", items)
    
    assert order.id == 1, f"Ошибка: id={order.id}"
    assert order.id_customers == 1, f"Ошибка: id_customers={order.id_customers}"
    assert order.date == "2025-04-20", f"Ошибка: date={order.date}"
    assert order.status == "новый", f"Ошибка: status={order.status}"
    assert len(order.items) == 2, f"Ошибка: items count={len(order.items)}"
    
    print(f"Заказ создан: ID={order.id}, клиент={order.id_customers}, дата={order.date}, статус={order.status}")
    return True


def test_order_total():
    print("\n" + "-"*50)
    print("6. ТЕСТ: Вычисление total заказа")

    items1 = [
        Items("Пицца", 2, 750),  
        Items("Кола", 1, 150)    
    ]
    order1 = Orders(1, 1, "2025-04-20", "новый", items1)
    assert order1.total == 1650, f"Ошибка: total={order1.total} (должно быть 1650)"
    
    items2 = [
        Items("Суши", 3, 200),    
        Items("Чай", 2, 100)      
    ]
    order2 = Orders(2, 1, "2025-04-21", "новый", items2)
    assert order2.total == 800, f"Ошибка: total={order2.total} (должно быть 800)"
    
    items3 = [Items("Кофе", 1, 250)]
    order3 = Orders(3, 2, "2025-04-22", "новый", items3)
    assert order3.total == 250, f"Ошибка: total={order3.total} (должно быть 250)"
    
    print(f"total заказов: заказ1={order1.total} руб., заказ2={order2.total} руб., заказ3={order3.total} руб.")
    return True


def test_order_date_obj():
    print("\n" + "-"*50)
    print("7. ТЕСТ: Преобразование даты в datetime")

    
    items = [Items("Пицца", 1, 500)]
    order = Orders(1, 1, "2025-04-20", "новый", items)
    
    assert isinstance(order.date_obj, datetime), f"Ошибка: date_obj не datetime"
    assert order.date_obj.year == 2025, f"Ошибка: year={order.date_obj.year}"
    assert order.date_obj.month == 4, f"Ошибка: month={order.date_obj.month}"
    assert order.date_obj.day == 20, f"Ошибка: day={order.date_obj.day}"
    
    print(f"date_obj работает: {order.date} -> {order.date_obj}")
    return True


def test_order_items_types():
    print("\n" + "-"*50)
    print("8. ТЕСТ: Типы товаров в заказе")
    
    items = [
        Items("Пицца", 2, 750),
        Items("Кола", 1, 150),
        Items("Чай", 3, 50)
    ]
    order = Orders(1, 1, "2025-04-20", "новый", items)
    
    for item in order.items:
        assert isinstance(item, Items), f"Ошибка: {item} не является Items"
        assert hasattr(item, 'product_name'), "Ошибка: нет product_name"
        assert hasattr(item, 'quantity'), "Ошибка: нет quantity"
        assert hasattr(item, 'price'), "Ошибка: нет price"
        assert hasattr(item, 'total'), "Ошибка: нет total"
    
    print(f"Все товары имеют правильные типы и атрибуты")
    return True


def test_empty_items_list():
    print("\n" + "-"*50)
    print("9. ТЕСТ: Пустой список товаров")
    
    order = Orders(1, 1, "2025-04-20", "новый", [])
    
    assert len(order.items) == 0, f"Ошибка: items count={len(order.items)}"
    assert order.total == 0, f"Ошибка: total={order.total} (должно быть 0)"
    
    print(f"Заказ без товаров: total={order.total} руб.")
    return True


def test_invalid_date_format():
    print("\n" + "-"*50)
    print("10. ТЕСТ: Неверный формат даты")
    
    items = [Items("Пицца", 1, 500)]
    
    try:
        order = Orders(1, 1, "20.04.2025", "новый", items)
        order.date_obj  
        print("Ошибка: неверный формат даты должен вызывать исключение")
        return False
    except ValueError:
        print(f"Неверный формат даты вызывает ошибку (как и ожидалось)")
        return True


def test_date_obj_setter():
    
    print("\n"+"-"*50)
    print("11. ТЕСТ: Установка даты через datetime")
    
    items = [Items("Пицца", 1, 500)]
    order = Orders(1, 1, "2025-04-20", "новый", items)
    
    new_date = datetime(2025, 12, 25)
    order.date_obj = new_date
    
    assert order.date == "2025-12-25", f"Ошибка: date={order.date}"
    assert order.date_obj == new_date, f"Ошибка: date_obj={order.date_obj}"
    
    print(f"Установка даты через datetime работает: {new_date} -> {order.date}")
    return True


def test_multiple_items_in_order():
    print("-"*50)
    print("12. ТЕСТ: Заказ с множеством товаров")
    
    items = [
        Items("Пицца", 2, 750),      
        Items("Кола", 2, 150),      
        Items("Чай", 3, 50),        
        Items("Суши", 1, 200),      
        Items("Кофе", 2, 100)        
    ]
    order = Orders(1, 1, "2025-04-20", "новый", items)
    
    expected_total = 1500 + 300 + 150 + 200 + 200 
    
    assert len(order.items) == 5, f"Ошибка: items count={len(order.items)}"
    assert order.total == expected_total, f"Ошибка: total={order.total} (должно быть {expected_total})"
    
    print(f"Заказ из 5 товаров: total={order.total} руб.")
    return True


def run_all_tests():
    print("\n" + "-"*50)
    
    tests = [
        ("Создание клиента", test_customer_creation),
        ("Обновление клиента", test_customer_update),
        ("Создание товара", test_item_creation),
        ("Вычисление total товара", test_item_total),
        ("Создание заказа", test_order_creation),
        ("Вычисление total заказа", test_order_total),
        ("Преобразование даты", test_order_date_obj),
        ("Типы товаров в заказе", test_order_items_types),
        ("Пустой список товаров", test_empty_items_list),
        ("Неверный формат даты", test_invalid_date_format),
        ("Установка даты через datetime", test_date_obj_setter),
        ("Заказ с множеством товаров", test_multiple_items_in_order),
    ]
    
    passed = 0
    failed = 0
    failed_tests = []
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"{name}")
        except AssertionError as e:
            failed += 1
            failed_tests.append(name)
            print(f"{name}: {e}")
        except Exception as e:
            failed += 1
            failed_tests.append(name)
            print(f"{name}: Ошибка - {e}")
    
    print("\n" + "-"*50)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print(f"Пройдено: {passed}")
    print(f"Не пройдено: {failed}")
    
    if failed_tests:
        print(f"\nУпавшие тесты:")
        for test_name in failed_tests:
            print(f"   - {test_name}")
    
    
    if failed == 0:
        print("ВСЕ ТЕСТЫ МОДЕЛЕЙ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(f"Есть ошибки! Пройдено {passed} из {passed + failed}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)