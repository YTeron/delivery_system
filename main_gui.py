import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
from pathlib import Path

from database import DatabaseManager
from data_export import DataExporter
from models import Customers, Orders, Items


class DeliverySystemGUI:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления доставкой")
        self.root.geometry("1300x750")
        
        self.db = DatabaseManager()
        self.exporter = DataExporter(self.db)
        
        self.setup_menu()
        self.setup_main_layout()
        
        self.refresh_customers()
        self.refresh_orders()
        self.refresh_reports()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт заказов в JSON", command=self.export_orders)
        file_menu.add_command(label="Импорт заказов из JSON", command=self.import_orders)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def setup_main_layout(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_customers_tab()
        self.setup_orders_tab()
        self.setup_reports_tab()
    
    def setup_customers_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Клиенты")
        
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Добавить", command=self.add_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Редактировать", command=self.edit_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Удалить", command=self.delete_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Обновить", command=self.refresh_customers).pack(side=tk.LEFT, padx=2)
        
        columns = ("ID", "Имя", "Телефон", "Адрес", "Заказов", "Потрачено")
        self.customers_tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=100 if col == "ID" else 150)
        
        self.customers_tree.column("Адрес", width=250)
        self.customers_tree.column("Потрачено", width=120)
        
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def refresh_customers(self):
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        for customer in self.db.get_all_customers():
            orders_count = len(self.db.get_orders_by_customer(customer.id))
            total_spent = self.db.get_customer_total_spent(customer.id)
            
            self.customers_tree.insert("", tk.END, values=(
                customer.id, customer.name, customer.phone, 
                customer.address, orders_count, f"{total_spent:.2f} руб."
            ))
    
    def add_customer(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление клиента")
        dialog.geometry("400x350")
        dialog.grab_set()
        
        fields = {}
        for i, (label, key) in enumerate([("ID:", "id"), ("Имя:", "name"), 
                                           ("Телефон:", "phone"), ("Адрес:", "address")]):
            ttk.Label(dialog, text=label).pack(pady=(10 if i == 0 else 5, 0))
            entry = ttk.Entry(dialog, width=40)
            entry.pack(pady=5)
            fields[key] = entry
        
        def save():
            try:
                customer_id = int(fields["id"].get())
                name = fields["name"].get()
                phone = fields["phone"].get()
                address = fields["address"].get()
                
                if not all([customer_id, name, phone, address]):
                    messagebox.showerror("Ошибка", "Заполните все поля")
                    return
                
                if self.db.get_customer(customer_id):
                    messagebox.showerror("Ошибка", f"Клиент с ID {customer_id} уже существует")
                    return
                
                customer = Customers(customer_id, name, phone, address)
                self.db.add_customer(customer)
                self.refresh_customers()
                dialog.destroy()
                messagebox.showinfo("Успех", "Клиент добавлен")
            except ValueError:
                messagebox.showerror("Ошибка", "ID должен быть числом")
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def edit_customer(self):
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите клиента")
            return
        
        values = self.customers_tree.item(selected[0])['values']
        customer_id = int(values[0])
        customer = self.db.get_customer(customer_id)
        if not customer:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование клиента")
        dialog.geometry("400x350")
        dialog.grab_set()
        
        ttk.Label(dialog, text="ID:").pack(pady=(10,0))
        id_entry = ttk.Entry(dialog, width=40)
        id_entry.insert(0, customer.id)
        id_entry.config(state='disabled')
        id_entry.pack(pady=5)
        
        fields = {}
        for label, key, value in [("Имя:", "name", customer.name), 
                                   ("Телефон:", "phone", customer.phone),
                                   ("Адрес:", "address", customer.address)]:
            ttk.Label(dialog, text=label).pack(pady=(10,0))
            entry = ttk.Entry(dialog, width=40)
            entry.insert(0, value)
            entry.pack(pady=5)
            fields[key] = entry
        
        def save():
            customer.name = fields["name"].get()
            customer.phone = fields["phone"].get()
            customer.address = fields["address"].get()
            
            if self.db.update_customer(customer):
                self.refresh_customers()
                dialog.destroy()
                messagebox.showinfo("Успех", "Клиент обновлен")
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def delete_customer(self):
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите клиента")
            return
        
        values = self.customers_tree.item(selected[0])['values']
        customer_id = int(values[0])
        customer_name = values[1]
        
        orders = self.db.get_orders_by_customer(customer_id)
        if orders:
            messagebox.showerror("Ошибка", f"Нельзя удалить клиента '{customer_name}'. У него есть {len(orders)} заказ(ов).")
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить клиента '{customer_name}'?"):
            if self.db.delete_customer(customer_id):
                self.refresh_customers()
                messagebox.showinfo("Успех", "Клиент удален")
    
    def setup_orders_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Заказы")
        
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Добавить", command=self.add_order).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Редактировать статус", command=self.edit_order_status).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Удалить", command=self.delete_order).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Обновить", command=self.refresh_orders).pack(side=tk.LEFT, padx=2)
        
        filter_frame = ttk.LabelFrame(tab, text="Фильтры")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        filter_inner = ttk.Frame(filter_frame)
        filter_inner.pack(pady=5)
        
        ttk.Label(filter_inner, text="Статус:").pack(side=tk.LEFT, padx=5)
        self.status_filter = ttk.Combobox(filter_inner, values=["Все", "новый", "в доставке", "выполнен", "отменён"], width=15)
        self.status_filter.set("Все")
        self.status_filter.pack(side=tk.LEFT, padx=5)
        self.status_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_orders())
        
        ttk.Label(filter_inner, text="Дата от:").pack(side=tk.LEFT, padx=5)
        self.date_from_entry = ttk.Entry(filter_inner, width=12)
        self.date_from_entry.pack(side=tk.LEFT, padx=5)
        self.date_from_entry.bind("<KeyRelease>", lambda e: self.refresh_orders())
        
        ttk.Label(filter_inner, text="Дата до:").pack(side=tk.LEFT, padx=5)
        self.date_to_entry = ttk.Entry(filter_inner, width=12)
        self.date_to_entry.pack(side=tk.LEFT, padx=5)
        self.date_to_entry.bind("<KeyRelease>", lambda e: self.refresh_orders())
        
        ttk.Button(filter_inner, text="Очистить", command=self.clear_filters).pack(side=tk.LEFT, padx=20)
        
        columns = ("ID", "Клиент", "Дата", "Статус", "Сумма", "Товаров")
        self.orders_tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=100)
        
        self.orders_tree.column("Клиент", width=150)
        self.orders_tree.column("Сумма", width=120)
        
        details_frame = ttk.LabelFrame(tab, text="Детали заказа")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.order_details_text = tk.Text(details_frame, height=8, wrap=tk.WORD)
        self.order_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        
        self.orders_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.orders_tree.bind("<<TreeviewSelect>>", self.show_order_details)
    
    def clear_filters(self):
        self.status_filter.set("Все")
        self.date_from_entry.delete(0, tk.END)
        self.date_to_entry.delete(0, tk.END)
        self.refresh_orders()
    
    def refresh_orders(self):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        orders = self.db.get_all_orders()
        
        status = self.status_filter.get()
        if status != "Все":
            orders = [o for o in orders if o.status == status]
        date_from = self.date_from_entry.get().strip()
        if date_from:
            orders = [o for o in orders if o.date >= date_from]
        
        date_to = self.date_to_entry.get().strip()
        if date_to:
            orders = [o for o in orders if o.date <= date_to]
        
        for order in orders:
            customer = self.db.get_customer(order.id_customers)
            customer_name = customer.name if customer else f"ID:{order.id_customers}"
            
            self.orders_tree.insert("", tk.END, values=(
                order.id, customer_name, order.date, order.status,
                f"{order.total:.2f} руб.", len(order.items)
            ))
    
    def show_order_details(self, event):
        selected = self.orders_tree.selection()
        if not selected:
            return
        
        values = self.orders_tree.item(selected[0])['values']
        order_id = int(values[0])
        order = self.db.get_order(order_id)
        
        if not order:
            return
        
        customer = self.db.get_customer(order.id_customers)
        
        details = f"ЗАКАЗ #{order.id}\n"
        details += "-"*50 + "\n"
        details += f"Клиент: {customer.name if customer else 'Неизвестен'}\n"
        details += f"Телефон: {customer.phone if customer else 'Неизвестен'}\n"
        details += f"Адрес: {customer.address if customer else 'Неизвестен'}\n"
        details += f"Дата: {order.date}\n"
        details += f"Статус: {order.status}\n"
        details += f"Сумма: {order.total:.2f} руб.\n"
        details += "\nТОВАРЫ:\n"
        
        for i, item in enumerate(order.items, 1):
            details += f"{i}. {item.product_name}: {item.quantity} x {item.price:.2f} = {item.total:.2f} руб.\n"
        
        self.order_details_text.delete(1.0, tk.END)
        self.order_details_text.insert(1.0, details)
    
    def add_order(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление заказа")
        dialog.geometry("550x650")
        dialog.grab_set()
        
        # ID заказа
        ttk.Label(dialog, text="ID заказа:").pack(pady=(10,0))
        id_entry = ttk.Entry(dialog)
        id_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Клиент:").pack(pady=(10,0))
        customers = self.db.get_all_customers()
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(dialog, textvariable=customer_var, width=40)
        customer_combo['values'] = [f"{c.id} - {c.name} ({c.phone})" for c in customers]
        customer_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Дата (YYYY-MM-DD):").pack(pady=(10,0))
        date_entry = ttk.Entry(dialog)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Статус:").pack(pady=(10,0))
        status_combo = ttk.Combobox(dialog, values=["новый", "в доставке", "выполнен", "отменён"])
        status_combo.set("новый")
        status_combo.pack(pady=5)
        
        items_frame = ttk.LabelFrame(dialog, text="Товары")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        items_listbox = tk.Listbox(items_frame, height=6)
        items_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        def add_item():
            item_dialog = tk.Toplevel(dialog)
            item_dialog.title("Добавить товар")
            item_dialog.geometry("400x250")
            item_dialog.grab_set()
            
            ttk.Label(item_dialog, text="Название:").pack(pady=(10,0))
            name_entry = ttk.Entry(item_dialog)
            name_entry.pack(pady=5)
            
            ttk.Label(item_dialog, text="Количество:").pack(pady=(10,0))
            quantity_entry = ttk.Entry(item_dialog)
            quantity_entry.pack(pady=5)
            
            ttk.Label(item_dialog, text="Цена:").pack(pady=(10,0))
            price_entry = ttk.Entry(item_dialog)
            price_entry.pack(pady=5)
            
            def save_item():
                name = name_entry.get()
                try:
                    quantity = int(quantity_entry.get())
                    price = float(price_entry.get())
                    items_listbox.insert(tk.END, f"{name}:{quantity}:{price}")
                    item_dialog.destroy()
                except ValueError:
                    messagebox.showerror("Ошибка", "Количество и цена должны быть числами")
            
            ttk.Button(item_dialog, text="Добавить", command=save_item).pack(pady=20)
        
        def remove_item():
            selected = items_listbox.curselection()
            if selected:
                items_listbox.delete(selected[0])
        
        btn_frame = ttk.Frame(items_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Добавить товар", command=add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить товар", command=remove_item).pack(side=tk.LEFT, padx=5)
        
        def save_order():
            try:
                order_id = int(id_entry.get())
                customer_str = customer_var.get()
                if not customer_str:
                    messagebox.showerror("Ошибка", "Выберите клиента")
                    return
                
                customer_id = int(customer_str.split(" - ")[0])
                order_date = date_entry.get()
                status = status_combo.get()
                
                if not self.db.get_customer(customer_id):
                    messagebox.showerror("Ошибка", "Клиент не найден")
                    return
                
                if self.db.get_order(order_id):
                    messagebox.showerror("Ошибка", f"Заказ с ID {order_id} уже существует")
                    return
                
                items = []
                for item_str in items_listbox.get(0, tk.END):
                    name, quantity, price = item_str.split(':')
                    items.append(Items(name, int(quantity), float(price)))
                
                if not items:
                    messagebox.showerror("Ошибка", "Добавьте хотя бы один товар")
                    return
                
                order = Orders(order_id, customer_id, order_date, status, items)
                self.db.add_order(order)
                self.refresh_orders()
                self.refresh_customers()
                self.refresh_reports()
                dialog.destroy()
                messagebox.showinfo("Успех", f"Заказ #{order_id} добавлен на сумму {order.total:.2f} руб.")
                
            except ValueError:
                messagebox.showerror("Ошибка", "ID должен быть числом")
        
        ttk.Button(dialog, text="💾 Сохранить заказ", command=save_order).pack(pady=20)
    
    def edit_order_status(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return
        
        values = self.orders_tree.item(selected[0])['values']
        order_id = int(values[0])
        current_status = values[3]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменение статуса")
        dialog.geometry("300x150")
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Заказ #{order_id}", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(dialog, text="Новый статус:").pack()
        
        status_combo = ttk.Combobox(dialog, values=["новый", "в доставке", "выполнен", "отменён"])
        status_combo.set(current_status)
        status_combo.pack(pady=5)
        
        def save():
            new_status = status_combo.get()
            if new_status and new_status != current_status:
                if self.db.update_order_status(order_id, new_status):
                    self.refresh_orders()
                    self.refresh_reports()
                    dialog.destroy()
                    messagebox.showinfo("Успех", f"Статус изменен на '{new_status}'")
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def delete_order(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return
        
        values = self.orders_tree.item(selected[0])['values']
        order_id = int(values[0])
        
        if messagebox.askyesno("Подтверждение", f"Удалить заказ #{order_id}?"):
            if self.db.delete_order(order_id):
                self.refresh_orders()
                self.refresh_customers()
                self.refresh_reports()
                self.order_details_text.delete(1.0, tk.END)
                messagebox.showinfo("Успех", f"Заказ #{order_id} удален")
    
    def setup_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Отчёты и аналитика")
        
        period_frame = ttk.LabelFrame(tab, text="Выбор периода")
        period_frame.pack(fill=tk.X, padx=10, pady=5)
        
        period_inner = ttk.Frame(period_frame)
        period_inner.pack(pady=10)
        
        ttk.Label(period_inner, text="Период:").pack(side=tk.LEFT, padx=5)
        self.period_var = tk.StringVar(value="week")
        ttk.Radiobutton(period_inner, text="День", variable=self.period_var, value="day", command=self.refresh_reports).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_inner, text="Неделя", variable=self.period_var, value="week", command=self.refresh_reports).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_inner, text="Месяц", variable=self.period_var, value="month", command=self.refresh_reports).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_inner, text="Всё время", variable=self.period_var, value="all", command=self.refresh_reports).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(period_inner, text="Показать отчёт", command=self.refresh_reports).pack(side=tk.LEFT, padx=20)

        reports_frame = ttk.Frame(tab)
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_frame = ttk.Frame(reports_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        status_frame = ttk.LabelFrame(left_frame, text="Количество заказов по статусам")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.status_stats_text = tk.Text(status_frame, height=8, wrap=tk.WORD)
        self.status_stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        top_frame = ttk.LabelFrame(left_frame, text="Топ-3 клиента по сумме заказов")
        top_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.top_customers_text = tk.Text(top_frame, height=6, wrap=tk.WORD)
        self.top_customers_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(reports_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        revenue_frame = ttk.LabelFrame(right_frame, text="Общая выручка")
        revenue_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.revenue_text = tk.Text(revenue_frame, height=8, wrap=tk.WORD, font=("Arial", 10))
        self.revenue_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        chart_frame = ttk.LabelFrame(right_frame, text="Динамика выручки по дням")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.chart_text = tk.Text(chart_frame, height=10, wrap=tk.WORD, font=("Courier", 9))
        self.chart_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def refresh_reports(self):
        period = self.period_var.get()
        orders = self.db.get_all_orders()
        filtered_orders = self.filter_by_period(orders, period)
        
        self.update_status_stats(filtered_orders)
        self.update_top_customers(filtered_orders)
        self.update_revenue_stats(filtered_orders, period)
        self.update_chart(filtered_orders)
    
    def filter_by_period(self, orders, period):
        if period == "all":
            return orders
        
        today = datetime.now().date()
        if period == "day":
            start = today.strftime("%Y-%m-%d")
        elif period == "week":
            start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        elif period == "month":
            start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            return orders
        
        return [o for o in orders if o.date >= start]
    
    def update_status_stats(self, orders):
        self.status_stats_text.delete(1.0, tk.END)
        status_count = {}
        for order in orders:
            status_count[order.status] = status_count.get(order.status, 0) + 1
        
        total = len(orders)
        stats = f"Всего заказов: {total}\n\n"
        
        for status in ["новый", "в доставке", "выполнен", "отменён"]:
            count = status_count.get(status, 0)
            percent = (count / total * 100) if total > 0 else 0
            stats += f"{status}: {count} шт. ({percent:.1f}%)\n"
        
        self.status_stats_text.insert(1.0, stats)
    
    def update_top_customers(self, orders):
        self.top_customers_text.delete(1.0, tk.END)
        customer_total = {}
        for order in orders:
            customer_total[order.id_customers] = customer_total.get(order.id_customers, 0) + order.total
        
        top = sorted(customer_total.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if not top:
            self.top_customers_text.insert(1.0, "Нет данных")
            return
        
        result = ""
        for i, (cust_id, total) in enumerate(top, 1):
            customer = self.db.get_customer(cust_id)
            name = customer.name if customer else f"ID:{cust_id}"
            result += f"{i}. {name}\n   Сумма: {total:,.2f} руб.\n   Заказов: {len([o for o in orders if o.id_customers == cust_id])}\n\n"
        
        self.top_customers_text.insert(1.0, result)
    
    def update_revenue_stats(self, orders, period):
        self.revenue_text.delete(1.0, tk.END)
        total = sum(order.total for order in orders)
        avg = total / len(orders) if orders else 0
        
        period_names = {"day": "ДЕНЬ", "week": "НЕДЕЛЮ", "month": "МЕСЯЦ", "all": "ВСЁ ВРЕМЯ"}
        
        result = f"ЗА {period_names.get(period, period)}\n"
        result += "-"*30 + "\n\n"
        result += f"Общая выручка: {total:,.2f} руб.\n\n"
        result += f"Средний чек: {avg:,.2f} руб.\n\n"
        result += f"Всего заказов: {len(orders)}"
        
        self.revenue_text.insert(1.0, result)
    
    def update_chart(self, orders):
        self.chart_text.delete(1.0, tk.END)
        if not orders:
            self.chart_text.insert(1.0, "Нет данных")
            return
        
        daily = {}
        for order in orders:
            daily[order.date] = daily.get(order.date, 0) + order.total
        
        dates = sorted(daily.keys())
        if len(dates) > 10:
            dates = dates[-10:]
        
        result = "Динамика выручки:\n" + "-"*50 + "\n"
        for date in dates:
            result += f"{date}: {daily[date]:>12,.2f} руб.\n"
        
        result += "-"*50 + f"\nИТОГО: {sum(daily.values()):,.2f} руб."
        
        self.chart_text.insert(1.0, result)
    
    def export_orders(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                self.exporter.export_to_json(filepath)
                messagebox.showinfo("Успех", f"Заказы экспортированы в {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def import_orders(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                # Проверка корректности JSON
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "orders" not in data:
                    raise ValueError("Файл не содержит заказов")
                
                clear = messagebox.askyesno("Подтверждение", "Очистить существующие данные перед импортом?")
                
                self.exporter.import_from_json(filepath, clear_existing=clear)
                self.refresh_orders()
                self.refresh_customers()
                self.refresh_reports()
                messagebox.showinfo("Успех", "Импорт завершен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")
    
    def show_about(self):
        messagebox.showinfo("О программе", 
            "Система управления доставкой\nВерсия: 2.0\n\n"
            "Функции:\n"
            "- Управление клиентами (CRUD)\n"
            "- Управление заказами (CRUD)\n"
            "- Фильтрация заказов по статусу и дате\n"
            "- Отчёты и аналитика\n"
            "- Экспорт/импорт JSON\n"
            "- Защита от удаления клиентов с заказами")
    
    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.db.close()
            self.root.destroy()


def main():
    root = tk.Tk()
    app = DeliverySystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()