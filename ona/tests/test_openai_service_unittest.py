"""
Юнит-тесты для сервиса OpenAI с использованием unittest
"""
import unittest
import asyncio
from unittest import mock
import sys
import os
import importlib

# Добавляем корневую директорию проекта в путь для импорта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Импортируем после настройки путей
from ona.core.services.openai_service import OpenAIService, openai_service
import openai
from ona.config.settings import settings

class TestOpenAIService(unittest.TestCase):
    """
    Класс для тестирования OpenAIService с использованием unittest
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Подготовка перед запуском всех тестов в классе
        """
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
    
    @classmethod
    def tearDownClass(cls):
        """
        Очистка после запуска всех тестов в классе
        """
        cls.loop.close()
    
    def setUp(self):
        """
        Подготовка перед каждым тестом
        """
        # Сохраняем оригинальное значение API ключа
        self.original_api_key = openai.api_key
        
        # Создаем патч для AsyncClient перед каждым тестом
        self.openai_async_client_patch = mock.patch('openai.AsyncClient')
        self.mock_async_client = self.openai_async_client_patch.start()
        
        # Настраиваем мок для клиента
        self.mock_client_instance = mock.AsyncMock()
        self.mock_client_instance.models.list = mock.AsyncMock(return_value=[])
        self.mock_async_client.return_value = self.mock_client_instance
    
    def tearDown(self):
        """
        Очистка после каждого теста
        """
        # Останавливаем патч
        self.openai_async_client_patch.stop()
        
        # Восстанавливаем оригинальное значение API ключа
        openai.api_key = self.original_api_key
    
    def test_init(self):
        """
        Тест инициализации сервиса OpenAI
        """
        # Патчим openai.api_key для тестирования
        with mock.patch('openai.api_key', None):
            # Создаем экземпляр сервиса
            service = OpenAIService()
            
            # Проверяем, что API ключ был установлен правильно
            self.assertEqual(openai.api_key, settings.OPENAI_API_KEY)
    
    def test_init_warns_on_empty_api_key(self):
        """
        Тест проверки логирования предупреждения при пустом API ключе
        """
        # Патчим API ключ в настройках на пустой
        with mock.patch('ona.config.settings.settings.OPENAI_API_KEY', ''):
            # Патчим логгер для проверки вызова warning
            with mock.patch('ona.core.services.openai_service.logger.warning') as mock_warning:
                # Создаем экземпляр сервиса
                service = OpenAIService()
                
                # Проверяем, что было зарегистрировано предупреждение
                mock_warning.assert_called_once_with("API ключ OpenAI не установлен в переменных окружения")
    
    def test_singleton_instance(self):
        """
        Тест проверки, что глобальный экземпляр сервиса OpenAI существует
        """
        # Проверяем, что openai_service является экземпляром OpenAIService
        self.assertIsInstance(openai_service, OpenAIService)
    
    def test_check_api_connection_success(self):
        """
        Тест успешного подключения к API OpenAI
        """
        # Создаем экземпляр сервиса
        service = OpenAIService()
        
        # Запускаем асинхронный метод проверки подключения
        result = self.loop.run_until_complete(service.check_api_connection())
        
        # Проверяем результат
        self.assertTrue(result)
        
        # Проверяем, что метод models.list был вызван
        self.mock_client_instance.models.list.assert_called_once()
    
    def test_check_api_connection_failure(self):
        """
        Тест неудачного подключения к API OpenAI
        """
        # Настраиваем мок для возвращения ошибки
        self.mock_client_instance.models.list = mock.AsyncMock(side_effect=Exception("API Error"))
        
        # Создаем экземпляр сервиса
        service = OpenAIService()
        
        # Запускаем асинхронный метод проверки подключения
        result = self.loop.run_until_complete(service.check_api_connection())
        
        # Проверяем результат
        self.assertFalse(result)
        
        # Проверяем, что метод models.list был вызван
        self.mock_client_instance.models.list.assert_called_once()
    
    def test_check_api_connection_no_api_key(self):
        """
        Тест проверки соединения без установленного API ключа
        """
        # Временно устанавливаем пустой API ключ
        with mock.patch('openai.api_key', ''):
            # Создаем экземпляр сервиса
            service = OpenAIService()
            
            # Запускаем асинхронный метод проверки подключения
            result = self.loop.run_until_complete(service.check_api_connection())
            
            # Проверяем результат
            self.assertFalse(result)
            
            # Проверяем, что метод models.list НЕ был вызван (т.к. проверка должна завершиться раньше)
            self.mock_client_instance.models.list.assert_not_called()
    
    def test_api_key_from_env(self):
        """
        Тест проверки использования API ключа из переменных окружения
        """
        # Проверяем, что API ключ используется из настроек
        test_api_key = 'test_api_key'
        with mock.patch('ona.config.settings.settings.OPENAI_API_KEY', test_api_key):
            # Перезагружаем модуль для применения изменений
            import ona.core.services.openai_service
            importlib.reload(ona.core.services.openai_service)
            
            # Создаем новый экземпляр сервиса
            service = ona.core.services.openai_service.OpenAIService()
            
            # Проверяем, что API ключ был установлен правильно
            self.assertEqual(openai.api_key, test_api_key)
            
            # Восстанавливаем исходное состояние модуля
            importlib.reload(ona.core.services.openai_service)
    
    def test_generate_profile_success(self):
        """
        Тест успешной генерации психологического профиля
        """
        # Мокаем openai.AsyncClient для тестирования без реального API ключа
        with mock.patch('openai.AsyncClient') as mock_async_client:
            # Настраиваем мок для возврата тестового ответа
            mock_client_instance = mock.AsyncMock()
            mock_chat_completions = mock.AsyncMock()
            mock_client_instance.chat.completions.create = mock_chat_completions
            
            # Создаем мок-ответ
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = "Тестовый профиль"
            mock_chat_completions.return_value = mock_response
            
            # Устанавливаем возвращаемое значение для AsyncClient
            mock_async_client.return_value = mock_client_instance
            
            # Создаем экземпляр сервиса
            service = OpenAIService()
            
            # Тестовые данные пользователя
            user_data = {
                "birth_date": "01.01.1990",
                "birth_time": "12:00",
                "birth_place": "Москва",
                "age": 33,
                "psychology_answers": {
                    "0": {
                        "question_text": "Тестовый вопрос 1",
                        "option_text": "Тестовый ответ 1"
                    },
                    "1": {
                        "question_text": "Тестовый вопрос 2",
                        "option_text": "Тестовый ответ 2"
                    }
                }
            }
            
            # Проверяем генерацию профиля
            profile = self.loop.run_until_complete(service.generate_profile(user_data))
            
            # Проверяем результат
            self.assertEqual(profile, "Тестовый профиль")
            
            # Проверяем что был вызван нужный метод с правильными параметрами
            mock_chat_completions.assert_called_once()
            args, kwargs = mock_chat_completions.call_args
            self.assertEqual(kwargs["model"], "gpt-4")
            self.assertEqual(len(kwargs["messages"]), 2)
            self.assertEqual(kwargs["messages"][0]["role"], "system")
            self.assertEqual(kwargs["messages"][1]["role"], "user")
    
    def test_generate_profile_no_api_key(self):
        """
        Тест генерации профиля без установленного API ключа
        """
        # Временно устанавливаем пустой API ключ
        with mock.patch('openai.api_key', ''):
            # Создаем экземпляр сервиса
            service = OpenAIService()
            
            # Тестовые данные пользователя
            user_data = {"psychology_answers": {}}
            
            # Проверяем генерацию профиля
            profile = self.loop.run_until_complete(service.generate_profile(user_data))
            
            # Проверяем результат
            self.assertIn("Невозможно сгенерировать профиль", profile)
    
    def test_generate_profile_api_error(self):
        """
        Тест обработки ошибки API при генерации профиля
        """
        # Мокаем openai.AsyncClient для имитации ошибки
        with mock.patch('openai.AsyncClient') as mock_async_client:
            # Настраиваем мок с ошибкой
            mock_client_instance = mock.AsyncMock()
            mock_client_instance.chat.completions.create = mock.AsyncMock(side_effect=Exception("API Error"))
            mock_async_client.return_value = mock_client_instance
            
            # Создаем экземпляр сервиса
            service = OpenAIService()
            
            # Тестовые данные пользователя
            user_data = {"psychology_answers": {}}
            
            # Проверяем генерацию профиля
            profile = self.loop.run_until_complete(service.generate_profile(user_data))
            
            # Проверяем результат
            self.assertIn("Произошла ошибка", profile)


if __name__ == '__main__':
    unittest.main() 