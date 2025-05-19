# ONA: AI-наставник для женщин

ONA — это платформа, использующая искусственный интеллект для предоставления персонализированной поддержки и советов женщинам.

## Структура проекта

```
/api        - API интерфейсы
/core       - Основная логика приложения
/config     - Конфигурационные файлы
/utils      - Вспомогательные утилиты
/tests      - Тесты для проверки функциональности
```

## Требования

Список необходимых зависимостей находится в файле `requirements.txt`.

## Установка и запуск

1. Клонируйте репозиторий
2. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
3. Настройте переменные окружения (создайте файл `.env` на основе примера ниже)
4. Запустите приложение:
   ```
   python run.py
   ```

## Переменные окружения

Создайте файл `.env` в корне проекта со следующими переменными:

```
# Supabase конфигурация
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_KEY=your-supabase-key

# OpenAI конфигурация
OPENAI_API_KEY=your-openai-api-key

# Telegram Bot конфигурация
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# 11Labs конфигурация
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Настройки приложения
DEBUG=True
ENVIRONMENT=development

# Настройки платежной системы
PAYMENT_PROVIDER_KEY=your-payment-provider-key
```

## Настройка OpenAI API

Для работы с OpenAI API необходимо:

1. Получить API ключ на сайте [OpenAI](https://platform.openai.com/)
2. Добавить полученный ключ в файл `.env` в переменную `OPENAI_API_KEY`
3. Проверить подключение к API с помощью запуска тестов:
   ```
   python tests/run_tests.py
   ```

## Тестирование

В проекте используются два фреймворка для тестирования:
- pytest - для функциональных тестов
- unittest - для модульных тестов

Для запуска тестов:
```
# Запуск всех тестов
python tests/run_tests.py

# Запуск только unittest тестов
python tests/run_tests.py unittest

# Запуск только pytest тестов
python tests/run_tests.py pytest
```

## Разработка

Проект находится в стадии активной разработки. 