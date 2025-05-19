"""
Скрипт для запуска тестов OpenAI API клиента
"""
import unittest
import pytest
import sys
import os

# Добавляем корневую директорию проекта в путь для импорта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def run_unittest_tests():
    """
    Запуск тестов с использованием unittest
    """
    print("Запуск тестов с использованием unittest...")
    # Обнаружение и запуск тестов в текущем каталоге
    loader = unittest.TestLoader()
    test_suite = loader.discover(os.path.dirname(__file__), pattern="test_*_unittest.py")
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    return result.wasSuccessful()

def run_pytest_tests():
    """
    Запуск тестов с использованием pytest
    """
    print("Запуск тестов с использованием pytest...")
    # Запуск pytest с текущего каталога
    result = pytest.main(["-v", os.path.dirname(__file__), "-k", "test_openai_service.py"])
    return result == 0

if __name__ == "__main__":
    print("Запуск тестов для OpenAI API клиента")
    
    # Проверяем, что указано, какие тесты запускать
    if len(sys.argv) > 1 and sys.argv[1] == "unittest":
        success = run_unittest_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == "pytest":
        success = run_pytest_tests()
    else:
        # По умолчанию запускаем оба типа тестов
        unittest_success = run_unittest_tests()
        print("\n" + "-" * 70 + "\n")
        pytest_success = run_pytest_tests()
        success = unittest_success and pytest_success

    # Выводим результат тестирования
    if success:
        print("\nВсе тесты пройдены успешно!")
        sys.exit(0)
    else:
        print("\nНекоторые тесты не прошли!")
        sys.exit(1) 