# Инструкция по созданию Telegram бота через BotFather

## 1. Создание бота с помощью BotFather

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather) в поиске
2. Отправьте команду `/newbot`
3. Следуйте инструкциям BotFather:
   - Введите имя бота (например, "ONA AI Наставник")
   - Введите username бота (должен заканчиваться на "bot", например "OnaAiBot")
4. BotFather выдаст вам токен API для вашего бота. **Сохраните его в надежном месте!**

## 2. Настройка описания и команд бота (опционально)

1. Используйте команду `/setdescription`, чтобы добавить описание для бота
2. Используйте команду `/setcommands`, чтобы настроить список команд:
   ```
   start - Начать общение с ботом
   help - Показать список доступных команд
   ```

## 3. Добавление токена в переменные окружения

1. Откройте файл `.env` в корне проекта (или создайте его, если он не существует)
2. Добавьте строку с токеном:
   ```
   TELEGRAM_BOT_TOKEN=ваш_токен_полученный_от_botfather
   ```

## 4. Проверка работы бота

1. Запустите ваше FastAPI приложение
2. Откройте бота в Telegram и отправьте команду `/start`
3. Бот должен ответить приветственным сообщением 