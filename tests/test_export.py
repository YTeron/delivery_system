import sys
import json
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import DatabaseManager
from data_export import DataExporter
from models import Customers, Orders, Items


class TestExportImport:
    def __init__(self):
        self.test_db_path = None
        self.db = None
        self.exporter = None
        self.temp_dir = None
    
    def setup(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.temp_dir) / "test_tinydb.json"
        
        self.db = DatabaseManager(str(self.test_db_path))
        self.exporter = DataExporter(self.db)
        
        self._create_test_data()
        
        print("Тестовая среда создана")
    
    def teardown(self):
        if self.db:
            self.db.close()
        
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        
        print("Тестовая среда очищена")
    
    def _create_test_data(self):
        self.customer1 = Customers(1, "Иван Петров", "+7-123-456-78-90", "Москва, ул. Примерная, д. 1")
        self.customer2 = Customers(2, "Елена Сидорова", "+7-987-654-32-10", "СПб, Невский пр., д. 10")
        self.customer3 = Customers(3, "Алексей Иванов", "+7-555-123-45-67", "Казань, ул. Центральная, д. 5")
        
        self.db.add_customer(self.customer1)
        self.db.add_customer(self.customer2)
        self.db.add_customer(self.customer3)
        
        items1 = [Items("Пицца Маргарита", 2, 750), Items("Кока-Кола", 1, 150)]
        self.order1 = Orders(1, 1, "2025-04-20", "новый", items1)
        
        items2 = [Items("Суши сет", 1, 1200), Items("Чай зеленый", 2, 100)]
        self.order2 = Orders(2, 2, "2025-04-21", "в доставке", items2)
        
        items3 = [Items("Бургер", 2, 350), Items("Картошка фри", 1, 150), Items("Кола", 2, 120)]
        self.order3 = Orders(3, 1, "2025-04-22", "выполнен", items3)
        
        self.db.add_order(self.order1)
        self.db.add_order(self.order2)
        self.db.add_order(self.order3)
        
        print("   Тестовые данные созданы:")
        print(f"   - Клиентов: 3")
        print(f"   - Заказов: 3")
    
    
    def test_export_all_data(self):
        print("\n" + "-"*50)
        print("1. ТЕСТ: Экспорт всех данных")
        
        export_file = Path(self.temp_dir) / "export_all.json"
        
        customers = self.db.get_all_customers()
        orders = self.db.get_all_orders()
        
        data = {
            "customers": [
                {"id": c.id, "name": c.name, "phone": c.phone, "address": c.address}
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
                        {"product_name": i.product_name, "quantity": i.quantity, "price": i.price}
                        for i in o.items
                    ]
                }
                for o in orders
            ]
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        assert export_file.exists(), "Файл экспорта не создан"
        
        with open(export_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert "customers" in loaded_data, "Нет секции customers"
        assert "orders" in loaded_data, "Нет секции orders"
        assert len(loaded_data["customers"]) == 3, f"Экспортировано {len(loaded_data['customers'])} клиентов, должно быть 3"
        assert len(loaded_data["orders"]) == 3, f"Экспортировано {len(loaded_data['orders'])} заказов, должно быть 3"
        
        print(f"Экспортировано {len(loaded_data['customers'])} клиентов и {len(loaded_data['orders'])} заказов")
        return True
    
    def test_export_customers_only(self):
        print("\n" + "-"*50)
        print("2. ТЕСТ: Экспорт только клиентов")
        
        export_file = Path(self.temp_dir) / "export_customers.json"
        
        customers = self.db.get_all_customers()
        data = {
            "export_date": "2025-01-01",
            "type": "customers",
            "customers": [
                {
                    "id": c.id,
                    "name": c.name,
                    "phone": c.phone,
                    "address": c.address
                }
                for c in customers
            ]
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "customers" in data, "Нет секции customers"
        assert len(data["customers"]) == 3, f"Экспортировано {len(data['customers'])} клиентов, должно быть 3"
        
        customer_ids = [c["id"] for c in data["customers"]]
        assert 1 in customer_ids, "Клиент 1 не найден"
        assert 2 in customer_ids, "Клиент 2 не найден"
        assert 3 in customer_ids, "Клиент 3 не найден"
        
        print(f"Экспортировано {len(data['customers'])} клиентов")
        return True
    
    def test_export_orders_only(self):
        print("\n" + "-"*50)
        print("3. ТЕСТ: Экспорт только заказов")
        
        export_file = Path(self.temp_dir) / "export_orders.json"
        
        orders = self.db.get_all_orders()
        data = {
            "export_date": "2025-01-01",
            "type": "orders",
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
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "orders" in data, "Нет секции orders"
        assert len(data["orders"]) == 3, f"Экспортировано {len(data['orders'])} заказов, должно быть 3"
        
        order_ids = [o["id"] for o in data["orders"]]
        assert 1 in order_ids, "Заказ 1 не найден"
        assert 2 in order_ids, "Заказ 2 не найден"
        assert 3 in order_ids, "Заказ 3 не найден"
        
        print(f"Экспортировано {len(data['orders'])} заказов")
        return True

    
    def test_import_into_empty_db(self):
        print("\n" + "-"*50)
        print("4. ТЕСТ: Импорт в пустую БД")

        new_db_path = Path(self.temp_dir) / "new_empty_db.json"
        new_db = DatabaseManager(str(new_db_path))
        new_exporter = DataExporter(new_db)
        
        export_file = Path(self.temp_dir) / "for_import.json"
        
        customers = self.db.get_all_customers()
        orders = self.db.get_all_orders()
        
        data = {
            "customers": [
                {"id": c.id, "name": c.name, "phone": c.phone, "address": c.address}
                for c in customers
            ],
            "orders": [
                {
                    "id": o.id,
                    "customer_id": o.id_customers,
                    "order_date": o.date,
                    "status": o.status,
                    "total": o.total,
                    "items": [{"product_name": i.product_name, "quantity": i.quantity, "price": i.price} for i in o.items]
                }
                for o in orders
            ]
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open(export_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        for cust in import_data["customers"]:
            if not new_db.get_customer(cust["id"]):
                new_db.add_customer(Customers(cust["id"], cust["name"], cust["phone"], cust["address"]))
        
        for order_data in import_data["orders"]:
            if not new_db.get_order(order_data["id"]):
                items = [Items(i["product_name"], i["quantity"], i["price"]) for i in order_data["items"]]
                new_db.add_order(Orders(order_data["id"], order_data["customer_id"], order_data["order_date"], order_data["status"], items))
        
        imported_customers = new_db.get_all_customers()
        imported_orders = new_db.get_all_orders()
        
        assert len(imported_customers) == 3, f"Импортировано {len(imported_customers)} клиентов, должно быть 3"
        assert len(imported_orders) == 3, f"Импортировано {len(imported_orders)} заказов, должно быть 3"
        
        new_db.close()
        print(f"Импортировано {len(imported_customers)} клиентов и {len(imported_orders)} заказов")
        return True
    
    def test_import_with_clear(self):
        print("\n" + "-"*50)
        print("5. ТЕСТ: Импорт с очисткой существующих данных")
        
        test_db_path = Path(self.temp_dir) / "test_clear_db.json"
        test_db = DatabaseManager(str(test_db_path))
        
        test_db.add_customer(Customers(99, "Старый клиент", "+7-000-000-00-00", "Старый адрес"))
        
        export_file = Path(self.temp_dir) / "clear_import.json"
        
        new_customers = [
            {"id": 1, "name": "Новый клиент", "phone": "+7-111-111-11-11", "address": "Новый адрес"}
        ]
        
        data = {"customers": new_customers, "orders": []}
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        test_db.customers_table.truncate()
        test_db.orders_table.truncate()
        
        with open(export_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        for cust in import_data["customers"]:
            test_db.add_customer(Customers(cust["id"], cust["name"], cust["phone"], cust["address"]))
        
        customers = test_db.get_all_customers()
        assert len(customers) == 1, f"После очистки осталось {len(customers)} клиентов, должно быть 1"
        assert customers[0].name == "Новый клиент", "Импортирован неверный клиент"
        
        test_db.close()
        print("Импорт с очисткой выполнен успешно")
        return True
    
    def test_import_duplicate_handling(self):
        print("\n" + "-"*50)
        print("6. ТЕСТ: Обработка дубликатов при импорте")
        
        dup_db_path = Path(self.temp_dir) / "dup_db.json"
        dup_db = DatabaseManager(str(dup_db_path))
        
        existing_customer = Customers(1, "Существующий", "+7-111-111-11-11", "Адрес")
        dup_db.add_customer(existing_customer)
        
        export_file = Path(self.temp_dir) / "dup_import.json"
        data = {
            "customers": [
                {"id": 1, "name": "Дубликат", "phone": "+7-222-222-22-22", "address": "Новый адрес"},
                {"id": 2, "name": "Новый клиент", "phone": "+7-333-333-33-33", "address": "Другой адрес"}
            ],
            "orders": []
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open(export_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        for cust in import_data["customers"]:
            if not dup_db.get_customer(cust["id"]):
                dup_db.add_customer(Customers(cust["id"], cust["name"], cust["phone"], cust["address"]))
        
        customers = dup_db.get_all_customers()
        assert len(customers) == 2, f"Ожидалось 2 клиента, получено {len(customers)}"
        
        original = dup_db.get_customer(1)
        assert original.name == "Существующий", "Существующий клиент был перезаписан!"
        
        dup_db.close()
        print("Дубликаты обработаны корректно")
        return True
    
    def test_validate_correct_json(self):
        print("\n" + "-"*50)
        print("7. ТЕСТ: Валидация корректного JSON")
        
        valid_file = Path(self.temp_dir) / "valid.json"
        data = {"customers": [], "orders": []}
        
        with open(valid_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        try:
            with open(valid_file, 'r', encoding='utf-8') as f:
                json.load(f)
            is_valid = True
        except:
            is_valid = False
        
        assert is_valid, "Корректный JSON определен как невалидный"
        print("Корректный JSON прошел валидацию")
        return True
    
    def test_validate_invalid_json(self):
        print("\n" + "-"*50)
        print("8. ТЕСТ: Валидация некорректного JSON")
        
        invalid_file = Path(self.temp_dir) / "invalid.json"
        with open(invalid_file, 'w', encoding='utf-8') as f:
            f.write("{некорректный json}")
        is_valid = True
        try:
            with open(invalid_file, 'r', encoding='utf-8') as f:
                json.load(f)
        except:
            is_valid = False
        
        assert not is_valid, "Некорректный JSON определен как валидный"
        print("Некорректный JSON правильно отклонен")
        return True
    
    def test_validate_missing_fields(self):
        print("\n" + "-"*50)
        print("9. ТЕСТ: Валидация отсутствующих полей")
        
        missing_file = Path(self.temp_dir) / "missing.json"
        data = {"wrong_field": []}
        
        with open(missing_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open(missing_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        has_orders = "orders" in loaded
        has_customers = "customers" in loaded
        
        assert not (has_orders or has_customers), "Файл без customers/orders должен быть невалидным"
        print("Отсутствие обязательных полей правильно обнаружено")
        return True
    
    def test_preserve_data_integrity(self):
        print("\n" + "-"*50)
        print("10. ТЕСТ: Сохранение целостности данных")
        
        source_db_path = Path(self.temp_dir) / "source.json"
        source_db = DatabaseManager(str(source_db_path))
        
        customer = Customers(10, "Тестовый клиент", "+7-999-999-99-99", "Тестовый адрес")
        source_db.add_customer(customer)
        
        items = [Items("Тестовый товар", 3, 100)]
        order = Orders(10, 10, "2025-06-12", "новый", items)
        source_db.add_order(order)
        
        export_file = Path(self.temp_dir) / "integrity_export.json"
        customers_data = source_db.get_all_customers()
        orders_data = source_db.get_all_orders()
        
        export_data = {
            "customers": [
                {"id": c.id, "name": c.name, "phone": c.phone, "address": c.address}
                for c in customers_data
            ],
            "orders": [
                {
                    "id": o.id,
                    "customer_id": o.id_customers,
                    "order_date": o.date,
                    "status": o.status,
                    "total": o.total,
                    "items": [{"product_name": i.product_name, "quantity": i.quantity, "price": i.price} for i in o.items]
                }
                for o in orders_data
            ]
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        source_db.close()
        
        dest_db_path = Path(self.temp_dir) / "dest.json"
        dest_db = DatabaseManager(str(dest_db_path))
        
        with open(export_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        for cust in import_data["customers"]:
            dest_db.add_customer(Customers(cust["id"], cust["name"], cust["phone"], cust["address"]))
        
        for order_data in import_data["orders"]:
            items = [Items(i["product_name"], i["quantity"], i["price"]) for i in order_data["items"]]
            dest_db.add_order(Orders(order_data["id"], order_data["customer_id"], order_data["order_date"], order_data["status"], items))
        
        imported_customer = dest_db.get_customer(10)
        imported_order = dest_db.get_order(10)
        
        assert imported_customer is not None, "Клиент не импортирован"
        assert imported_order is not None, "Заказ не импортирован"
        assert imported_customer.name == "Тестовый клиент", "Имя клиента не совпадает"
        assert imported_order.total == 300, f"Сумма заказа {imported_order.total} != 300"
        assert imported_order.items[0].product_name == "Тестовый товар", "Товар не совпадает"
        
        dest_db.close()
        print("Целостность данных сохранена")
        return True
    
    
    def run_all_tests(self):        
        tests = [
            ("Экспорт всех данных", self.test_export_all_data),
            ("Экспорт только клиентов", self.test_export_customers_only),
            ("Экспорт только заказов", self.test_export_orders_only),
            ("Импорт в пустую БД", self.test_import_into_empty_db),
            ("Импорт с очисткой", self.test_import_with_clear),
            ("Обработка дубликатов", self.test_import_duplicate_handling),
            ("Валидация корректного JSON", self.test_validate_correct_json),
            ("Валидация некорректного JSON", self.test_validate_invalid_json),
            ("Валидация отсутствующих полей", self.test_validate_missing_fields),
            ("Сохранение целостности данных", self.test_preserve_data_integrity),
        ]
        
        passed = 0
        failed = 0
        failed_tests = []
        
        try:
            self.setup()
            
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
        
        except Exception as e:
            print(f"\nКритическая ошибка: {e}")
        
        finally:
            self.teardown()
        
        print("\n" + "-"*60)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print(f"Пройдено: {passed}")
        print(f"Не пройдено: {failed}")
        
        if failed_tests:
            print(f"\nУпавшие тесты:")
            for test_name in failed_tests:
                print(f"   - {test_name}")
        
        print("-"*50)
        
        if failed == 0:
            print("ВСЕ ТЕСТЫ ЭКСПОРТА/ИМПОРТА ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print(f"Есть ошибки! Пройдено {passed} из {passed + failed}")
        
        return failed == 0


if __name__ == "__main__":
    tester = TestExportImport()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)