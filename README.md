# Инструкция по запуску автоматических тестов

## Выполнять команды в терминале, по шагам, из корня проекта avitoQA

Создание виртуального окружения
1. python3 -m venv venv

Вход в виртуальное окружение
2. .\venv\Scripts\activate

Установка зависимостей
3. pip install .\data\requirements.txt

Запуск автоматических тестов
4. pytest tests/


# Для запуска тестов в allure отчетом

Запуск тестов с записью результатов
5. pytest tests/ --alluredir=allure-results -v

Генерация отчёта
6. allure generate allure-results -o allure-report --clean

Открытие в браузере
7. allure open allure-report

## Пример получившегося отчета см. ./screens_allure


# Команды для запуска линтеров

## Выполнять команды в терминале, по шагам, из корня проекта avitoQA

