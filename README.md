# Система управления доставкой

Система для управления заказами и клиентами службы доставки. Включает графический интерфейс (Tkinter) и командную строку (CLI).

## Оглавление
[Технологии](#технологии)
[Установка](#установка)
[Запуск](#запуск)
[Тестирование](#тестирование)
[Структура проекта](#структура-проекта)
[Автор](#автор)


## Технологии

| Компонент | Технология | Примечание |
|-----------|------------|------------|
| Язык      | Python 3.8+|            |
| GUI       | Tkinter    | Встроенный модуль |
| База данных | TinyDB   | Устанавливается через pip |
| Тестирование| pytest   | Устанавливается через pip |
| Логирование | logging  | Встроенный модуль         |
| Работа с JSON | json   | Встроенный модуль         |

#### Установка
python -m venv .venv
.venv\Scripts\activate
  ## Установка зависимостей
  PS <.../delivery_system> pip install pytest
  pip install tinydb
## Запуск
 # GUI режим (рекомендуется для пользователей)
python main_gui.py
 # CLI режим (для автоматизации)
python main_cli.py --help
## Тестирование
  # Тестирование базы данных
  pytest tests/test_database.py
  # Тестирование моделей
  pytest tests/test_models.py
  # Тестирование экспорта/импорта
  pytest tests/test_export.py
delivery_system/
│
├── main_gui.py # GUI-точка входа (Tkinter)
├── main_cli.py # CLI-точка входа (argparse)
├── database.py # Работа с БД (TinyDB)
├── models.py # Модели данных (Customers, Orders, Items)
├── data_export.py # Экспорт/импорт JSON
├── logger_config.py # Настройка логирования
├── requirements.txt # Зависимости проекта
├── README.md # Инструкция по установке и запуску
│
├── data/ # Папка с данными
│ └── tinydb.json # База данных (создаётся автоматически)
│
├── logs/ # Папка с логами
│ └── delivery_system_20250613.log
│
└── tests/ # Папка с тестами
├── test_database.py # Тесты БД
├── test_models.py # Тесты моделей
└── test_export.py # Тесты экспорта/импорта
### Автор
Трусов Артём Олегович
```bash
git 
cd delivery-system
