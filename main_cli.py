import argparse
import sys
from pathlib import Path

from database import DatabaseManager
from data_export import DataExporter
from models import Customers, Orders, Items


class CLIApp:
    
    def __init__(self):
        self.db = DatabaseManager()
        self.exporter = DataExporter(self.db)
    
    def close(self):
        self.db.close()
    
    def add_customer(self, args):
        if self.db.is_customer(args.id):
            print(f"Клиент с ID {args.id} уже существует")
            return
        
        customer = Customers(args.id, args.name, args.phone, args.address)
        self.db.add_customer(customer)
        print(f"Клиент добавлен (ID: {args.id})")
    
    def get_customer(self, args):
        customer = self.db.get_customer(args.id)
        if customer:
            print(f"\nИнформация о клиенте:")
            print(f"   ID: {customer.id}")
            print(f"   Имя: {customer.name}")
            print(f"   Телефон: {customer.phone}")
            print(f"   Адрес: {customer.address}")
            
            orders = self.db.get_orders_by_customer(customer.id)
            if orders:
                print(f"\nЗаказы ({len(orders)}):")
                total_sum = 0
                for order in orders:
                    print(f"   - Заказ #{order.id}: {order.status}, сумма: {order.total} руб.")
                    total_sum += order.total
                print(f"\nПотрачено: {total_sum} руб.")
            else:
                print(f"\nЗаказов нет")
        else:
            print(f"Клиент с ID {args.id} не найден")
    
    def list_customers(self, args):
        customers = self.db.get_all_customers()
        if not customers:
            print("Клиенты не найдены")
            return
        
        print(f"\n📋 Список клиентов ({len(customers)}):")
        print("-" * 60)
        for customer in customers:
            orders_count = len(self.db.get_orders_by_customer(customer.id))
            total_spent = self.db.get_customer_total_spent(customer.id)
            print(f"ID: {customer.id} | {customer.name} | {customer.phone}")
            print(f"    Адрес: {customer.address}")
            print(f"    Заказов: {orders_count} | Потрачено: {total_spent} руб.")
    
    def update_customer(self, args):
        customer = self.db.get_customer(args.id)
        if not customer:
            print(f"Клиент с ID {args.id} не найден")
            return
        
        if args.name:
            customer.name = args.name
        if args.phone:
            customer.phone = args.phone
        if args.address:
            customer.address = args.address
        
        if self.db.update_customer(customer):
            print(f"Клиент ID {args.id} обновлен")
        else:
            print(f"Ошибка при обновлении")
    
    def delete_customer(self, args):
        customer = self.db.get_customer(args.id)
        if not customer:
            print(f"Клиент с ID {args.id} не найден")
            return
        
        orders = self.db.get_orders_by_customer(args.id)
        if orders and not args.force:
            print(f"У клиента {len(orders)} заказ(ов). Используйте --force")
            return
        
        if args.force and orders:
            for order in orders:
                self.db.delete_order(order.id)
            print(f"Удалено заказов: {len(orders)}")
        
        if self.db.delete_customer(args.id):
            print(f"Клиент ID {args.id} удален")
    
    
    def add_order(self, args):
        if not self.db.is_customer(args.customer_id):
            print(f"Клиент с ID {args.customer_id} не найден")
            return
        
        if self.db.get_order(args.id):
            print(f"Заказ с ID {args.id} уже существует")
            return
        
        items = []
        for item_str in args.items.split(','):
            try:
                product_name, quantity, price = item_str.split(':')
                items.append(Items(
                    product_name=product_name.strip(),
                    quantity=int(quantity),
                    price=float(price)
                ))
            except ValueError:
                print(f"Ошибка в формате: {item_str}")
                print(f"   Используйте: название:количество:цена")
                return
        
        if not items:
            print("Заказ должен содержать хотя бы один товар")
            return
        
        order = Orders(args.id, args.customer_id, args.date, args.status, items)
        self.db.add_order(order)
        print(f"Заказ добавлен (ID: {args.id})")
        print(f"   Сумма: {order.total} руб.")
    
    def get_order(self, args):
        order = self.db.get_order(args.id)
        if not order:
            print(f"Заказ с ID {args.id} не найден")
            return
        
        customer = self.db.get_customer(order.id_customers)
        
        print(f"\nЗАКАЗ #{order.id}")
        print("-" * 50)
        print(f"   Статус: {order.status}")
        print(f"   Дата: {order.date}")
        print(f"   Клиент: {customer.name if customer else 'Неизвестен'}")
        print(f"   Сумма: {order.total} руб.")
        print(f"\n   Товары:")
        for i, item in enumerate(order.items, 1):
            print(f"      {i}. {item.product_name}: {item.quantity} x {item.price} = {item.total} руб.")
    
    def list_orders(self, args):
        orders = self.db.get_all_orders()
        if not orders:
            print("Заказы не найдены")
            return
        
        if args.status:
            orders = [o for o in orders if o.status == args.status]
        if args.customer_id:
            orders = [o for o in orders if o.customer_id == args.customer_id]
        
        if not orders:
            print("Заказы не найдены")
            return
        
        print(f"\nСписок заказов ({len(orders)}):")
        print("-" * 50)
        for order in orders:
            customer = self.db.get_customer(order.id_customers)
            customer_name = customer.name if customer else "Неизвестен"
            print(f"Заказ #{order.id} | {order.status} | {order.date}")
            print(f"   Клиент: {customer_name} | Сумма: {order.total} руб. | Товаров: {len(order.items)}")
            print("-" * 50)
    
    def update_order_status(self, args):
        order = self.db.get_order(args.id)
        if not order:
            print(f"Заказ с ID {args.id} не найден")
            return
        
        if self.db.update_order_status(args.id, args.status):
            print(f"Статус заказа #{args.id} изменен на '{args.status}'")
        else:
            print(f"Ошибка при обновлении")
    
    def delete_order(self, args):
        order = self.db.get_order(args.id)
        if not order:
            print(f"Заказ с ID {args.id} не найден")
            return
        
        if self.db.delete_order(args.id):
            print(f"Заказ #{args.id} удален")
    
    def export_data(self, args):
        self.exporter.export_to_json(args.output)
    
    def import_data(self, args):
        if not Path(args.file).exists():
            print(f"Файл {args.file} не найден")
            return
        self.exporter.import_from_json(args.file, clear_existing=args.clear)
    
    def search_orders(self, args):
        orders = self.db.search_orders_by_product(args.product)
        if not orders:
            print(f"Заказы с товаром '{args.product}' не найдены")
            return
        
        print(f"\nНайдено заказов: {len(orders)}")
        print("=" * 60)
        for order in orders:
            customer = self.db.get_customer(order.id_customers)
            print(f"Заказ #{order.id} | {order.status} | {order.total} руб.")
            print(f"  Клиент: {customer.name if customer else 'Неизвестен'}")
            for item in order.items:
                if item.product_name == args.product:
                    print(f" {item.product_name}: {item.quantity} x {item.price} = {item.total} руб.")
            print("-" * 60)
    
    def stats(self, args):
        customers = self.db.get_all_customers()
        orders = self.db.get_all_orders()
        
        print("\n" + "-" * 50)
        print(f"Клиентов: {len(customers)}")
        print(f"Заказов: {len(orders)}")
        
        if orders:
            total_revenue = sum(order.total for order in orders)
            avg_order = total_revenue / len(orders)
            print(f"Выручка: {total_revenue:,.2f} руб.")
            print(f"Средний чек: {avg_order:,.2f} руб.")
            
            statuses = {}
            for order in orders:
                statuses[order.status] = statuses.get(order.status, 0) + 1
            
            print(f"\nСтатусы:")
            for status, count in statuses.items():
                print(f"   {status}: {count}")
            
            products = {}
            for order in orders:
                for item in order.items:
                    products[item.product_name] = products.get(item.product_name, 0) + item.quantity
            
            print(f"\nТоп товаров:")
            for product, count in sorted(products.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {product}: {count} шт.")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Система управления доставкой",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Клиенты
  python main_cli.py customer add --id 1 --name "Иван" --phone "+7-123-456-78-90" --address "Москва"
  python main_cli.py customer get --id 1
  python main_cli.py customer list
  python main_cli.py customer update --id 1 --name "Иван Иванов"
  python main_cli.py customer delete --id 1 --force

  # Заказы
  python main_cli.py order add --id 1 --customer-id 1 --date "2025-04-20" --status "новый" --items "Пицца:2:750,Кола:1:150"
  python main_cli.py order get --id 1
  python main_cli.py order list --status "выполнен"
  python main_cli.py order update-status --id 1 --status "выполнен"
  python main_cli.py order delete --id 1

  # Экспорт/Импорт
  python main_cli.py export
  python main_cli.py export --output data/backup.json
  python main_cli.py import --file data/export.json
  python main_cli.py import --file data/backup.json --clear

  # Поиск и статистика
  python main_cli.py search --product "Пицца"
  python main_cli.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    cust_parser = subparsers.add_parser(
        'customer', 
        help='Управление клиентами',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python main_cli.py customer add --id 1 --name "Иван" --phone "+7-123-456-78-90" --address "Москва"
  python main_cli.py customer get --id 1
  python main_cli.py customer list
  python main_cli.py customer update --id 1 --name "Иван Иванов"
  python main_cli.py customer delete --id 1 --force
        """
    )
    cust_sub = cust_parser.add_subparsers(dest='action', help='Действия')
    
    add_cust = cust_sub.add_parser('add', help='Добавить клиента')
    add_cust.add_argument('--id', type=int, required=True, help='ID клиента')
    add_cust.add_argument('--name', required=True, help='Имя клиента')
    add_cust.add_argument('--phone', required=True, help='Телефон')
    add_cust.add_argument('--address', required=True, help='Адрес')
    
    get_cust = cust_sub.add_parser('get', help='Получить клиента')
    get_cust.add_argument('--id', type=int, required=True, help='ID клиента')
    
    cust_sub.add_parser('list', help='Список клиентов')
    
    upd_cust = cust_sub.add_parser('update', help='Обновить клиента')
    upd_cust.add_argument('--id', type=int, required=True, help='ID клиента')
    upd_cust.add_argument('--name', help='Новое имя')
    upd_cust.add_argument('--phone', help='Новый телефон')
    upd_cust.add_argument('--address', help='Новый адрес')
    
    del_cust = cust_sub.add_parser('delete', help='Удалить клиента')
    del_cust.add_argument('--id', type=int, required=True, help='ID клиента')
    del_cust.add_argument('--force', action='store_true', help='Принудительное удаление с заказами')
    order_parser = subparsers.add_parser(
        'order',
        help='Управление заказами',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python main_cli.py order add --id 1 --customer-id 1 --date "2025-04-20" --status "новый" --items "Пицца:2:750,Кола:1:150"
  python main_cli.py order get --id 1
  python main_cli.py order list --status "выполнен"
  python main_cli.py order update-status --id 1 --status "выполнен"
  python main_cli.py order delete --id 1
        """
    )
    order_sub = order_parser.add_subparsers(dest='action', help='Действия')
    
    add_order = order_sub.add_parser('add', help='Добавить заказ')
    add_order.add_argument('--id', type=int, required=True, help='ID заказа')
    add_order.add_argument('--customer-id', type=int, required=True, help='ID клиента')
    add_order.add_argument('--date', required=True, help='Дата заказа (YYYY-MM-DD)')
    add_order.add_argument('--status', default='новый', help='Статус заказа')
    add_order.add_argument('--items', required=True, help='Товары в формате: "название:кол-во:цена,название2:кол-во2:цена2"')
    
    get_order = order_sub.add_parser('get', help='Получить заказ')
    get_order.add_argument('--id', type=int, required=True, help='ID заказа')
    
    list_orders = order_sub.add_parser('list', help='Список заказов')
    list_orders.add_argument('--status', help='Фильтр по статусу')
    list_orders.add_argument('--customer-id', type=int, help='Фильтр по клиенту')
    
    upd_status = order_sub.add_parser('update-status', help='Обновить статус')
    upd_status.add_argument('--id', type=int, required=True, help='ID заказа')
    upd_status.add_argument('--status', required=True, help='Новый статус')
    
    del_order = order_sub.add_parser('delete', help='Удалить заказ')
    del_order.add_argument('--id', type=int, required=True, help='ID заказа')
    
    export_parser = subparsers.add_parser(
        'export',
        help='Экспорт данных',
        epilog="Пример: python main_cli.py export --output data/backup.json"
    )
    export_parser.add_argument('--output', default='data/export.json', help='Выходной файл')
    
    import_parser = subparsers.add_parser(
        'import',
        help='Импорт данных',
        epilog="Пример: python main_cli.py import --file data/export.json --clear"
    )
    import_parser.add_argument('--file', required=True, help='JSON файл для импорта')
    import_parser.add_argument('--clear', action='store_true', help='Очистить существующие данные')
    
    search_parser = subparsers.add_parser(
        'search',
        help='Поиск по товару',
        epilog="Пример: python main_cli.py search --product Пицца"
    )
    search_parser.add_argument('--product', required=True, help='Название товара')
    
    subparsers.add_parser('stats', help='Статистика')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    app = CLIApp()
    
    try:
        if args.command == 'customer':
            if args.action == 'add':
                app.add_customer(args)
            elif args.action == 'get':
                app.get_customer(args)
            elif args.action == 'list':
                app.list_customers(args)
            elif args.action == 'update':
                app.update_customer(args)
            elif args.action == 'delete':
                app.delete_customer(args)
        
        elif args.command == 'order':
            if args.action == 'add':
                app.add_order(args)
            elif args.action == 'get':
                app.get_order(args)
            elif args.action == 'list':
                app.list_orders(args)
            elif args.action == 'update-status':
                app.update_order_status(args)
            elif args.action == 'delete':
                app.delete_order(args)
        
        elif args.command == 'export':
            app.export_data(args)
        
        elif args.command == 'import':
            app.import_data(args)
        
        elif args.command == 'search':
            app.search_orders(args)
        
        elif args.command == 'stats':
            app.stats(args)
    
    except KeyboardInterrupt:
        print("\nПрервано")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    finally:
        app.close()


if __name__ == "__main__":
    main()