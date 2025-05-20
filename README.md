# ONA Telegram Bot

ONA – это персональный телеграм-бот наставник для задач профайлинга и общения.

## Установка и запуск

### Требования
- Python 3.10+
- pip (менеджер пакетов Python)
- Telegram Bot Token (получить у @BotFather)
- Supabase проект для базы данных

### Установка зависимостей

```bash
pip install -r requirements.txt
```

Или установка конкретных версий для совместимости:

```bash
pip install python-telegram-bot==20.7 supabase==2.8.1 python-dotenv httpx
```

### Настройка окружения
1. Создайте файл `.env` в корневой директории проекта
2. Добавьте в файл следующие переменные:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SECRET_TOKEN=your_secret_token_for_webhook
```

Или вы можете использовать тестовый конфигурационный файл в директории `ona/config/test.env`.

### Запуск бота

#### Запуск из корневой директории
```bash
python run_bot.py
```

#### Запуск из директории ona

##### В Linux/macOS:
```bash
cd ona
./start_bot.sh --polling
```

##### В Windows (PowerShell):
```powershell
cd ona
.\start_bot.ps1 -p
```

##### В Windows (CMD):
```cmd
cd ona
start_bot.bat -p
# или для быстрого запуска с переменными окружения
run_simple_polling.bat
```

### Тестирование

#### Тест подключения к Telegram API
```bash
python test_bot.py
```

#### Тестирование профайлинга (задача #3.1)

Для изолированного тестирования без подключения к базе данных:
```bash
cd ona
python test_profiling_solo.py
```

Для тестирования с реальной базой данных:
```bash
cd ona
python test_profiling.py
```

## Архитектура проекта

### Структура каталогов
```
ona/
├── api/             # API модули для внешнего взаимодействия
├── config/          # Конфигурации и настройки
├── core/            # Ядро бота
│   ├── db/          # Модули для работы с базой данных
│   ├── fsm/         # Машина конечных состояний
│   │   ├── handlers/# Обработчики состояний
│   └── services/    # Сервисы для бизнес-логики
├── docs/            # Документация
├── utils/           # Вспомогательные утилиты
```

### Ключевые модули
- `profiling_natal_handler.py` - Обработчик для сбора натальных данных (дата рождения, время, место, возраст)
- `state_router.py` - Маршрутизатор состояний пользователя
- `profile_service.py` - Сервис для работы с профилями пользователей
- `telegram_service.py` - Сервис для взаимодействия с Telegram API

## Задача #3.1: Натальный профайлинг

Реализована первая часть профайлинга - сбор натальной информации:
- Дата рождения
- Время рождения (если известно)
- Место рождения
- Возраст

## Проверка реализации

Для проверки реализации задачи #3.1 доступно несколько способов:

1. Запуск полноценного бота (требуется настройка Telegram Bot Token и Supabase)
2. Запуск изолированного теста `test_profiling_solo.py`, который не требует внешних подключений и проверяет логику профайлинга

Успешное выполнение теста подтверждает корректность реализации задачи #3.1.

## Лицензия
Проект разрабатывается для частного использования. # trigger
# restart
# restart
# restart
# restart
# deploy test
# restart deploy
# restart again
