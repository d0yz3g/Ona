"""
Пример использования OpenAI API клиента для проверки соединения
"""
import asyncio
import sys
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Добавляем корневую директорию проекта в путь для импорта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Импортируем сервис OpenAI
from ona.core.services.openai_service import openai_service

async def check_openai_api():
    """
    Проверка соединения с OpenAI API
    """
    logging.info("Проверка соединения с OpenAI API...")
    
    # Проверяем соединение с API
    is_connected = await openai_service.check_api_connection()
    
    if is_connected:
        logging.info("✓ Соединение с OpenAI API успешно установлено")
        return True
    else:
        logging.error("✗ Не удалось установить соединение с OpenAI API")
        logging.error("Убедитесь, что вы указали правильный API ключ в файле .env")
        return False

async def main():
    """
    Основная функция примера
    """
    logging.info("Запуск примера использования OpenAI API клиента")
    
    # Проверяем соединение с API
    api_connected = await check_openai_api()
    
    # Выводим результат
    if api_connected:
        logging.info("OpenAI API клиент настроен корректно")
    else:
        logging.error("Не удалось настроить OpenAI API клиент")
        sys.exit(1)


if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main()) 