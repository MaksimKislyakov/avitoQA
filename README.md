# Тестирование API Avito Internship

## 📋 Требования
- Python 3.10+
- `pip`
- `allure` CLI
- *(Опционально)* `make` для сокращения команд

## Перед выполнением каких либо инструкций - в терминале выполнить команды из корня проекта avitoQA/:
```bash
# Создание виртуального окружения в зависимости от вашей версии python
1. python3 -m venv venv
# или
1. python -m venv venv
# или
1. py -m venv venv

# Активация
# Windows:
2. venv\Scripts\activate
# или
# Linux/macOS:
2. source venv/bin/activate

# Установка зависимостей
3. pip install .\data\requirements.txt
```


## Инструкция по запуску автоматических тестов

### Выполнять команды в терминале, из корня проекта avitoQA/
#### Если установлен make, то можно использовать команду из терминала: make tests
```bash
# Запуск автоматических тестов
4. pytest tests/ -v
```


## Для запуска тестов в allure отчетом

### Пример получившегося отчета см. ./screens_allure
#### Если установлен make, то можно использовать команду из терминала: make tests_allure
```bash
# Запуск тестов с записью результатов
5. pytest tests/ --alluredir=allure-results -v

# Генерация отчёта
6. allure generate allure-results -o allure-report --clean

# Открытие в браузере
7. allure open allure-report
```


## Команды для запуска линтеров

### Выполнять команды в терминале, по шагам, из корня проекта avitoQA
#### Если установлен make, то можно использовать команду из терминала: make lint
```bash
# Форматирование кода (Black)
black .

# Линтинг и сортировка импортов (Ruff)
ruff check .
# Автоисправление простых проблем (сортировка импортов, удаление неиспользуемого)
ruff check . --fix

# Статическая проверка типов (Mypy)
mypy .
```
