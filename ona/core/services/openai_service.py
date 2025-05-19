"""
Сервис для работы с OpenAI API
"""
import logging
import os
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from datetime import datetime
from core.db.supabase_client import supabase

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Сервис для работы с OpenAI API
    """
    def __init__(self):
        """
        Инициализация сервиса OpenAI
        """
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-turbo-preview"  # Используем самую последнюю модель
        self.max_tokens = 2000  # Максимальная длина ответа
        self.temperature = 0.7  # Температура для генерации
        
        # Системный промпт для AI-наставника
        self.system_prompt = """Ты - ONA, AI-наставник для женщин. Твоя задача - помогать женщинам в их личностном росте, 
        саморазвитии и достижении гармонии. Ты используешь комбинацию психологии, астрологии и духовных практик.
        
        Основные принципы:
        1. Всегда поддерживай и проявляй эмпатию
        2. Используй мягкий, дружелюбный тон
        3. Давай конкретные, практические советы
        4. Уважай личные границы и конфиденциальность
        5. Не давай медицинских рекомендаций
        6. Не давай финансовых советов
        
        Формат ответов:
        - Используй эмодзи для создания теплой атмосферы
        - Разбивай длинные ответы на абзацы
        - Задавай уточняющие вопросы, когда нужно
        - Предлагай практические упражнения, когда уместно"""
    
    async def get_conversation_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Получение истории диалога пользователя
        
        Args:
            user_id: ID пользователя
            limit: Количество последних сообщений
            
        Returns:
            List[Dict]: Список сообщений в формате для OpenAI
        """
        try:
            # Получаем историю из базы данных
            response = supabase.table("conversations") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            if not response.data:
                return []
            
            # Преобразуем сообщения в формат для OpenAI
            messages = []
            for msg in reversed(response.data):  # Разворачиваем для хронологического порядка
                role = "user" if msg["is_user"] else "assistant"
                messages.append({
                    "role": role,
                    "content": msg["message_text"]
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Ошибка при получении истории диалога: {e}")
            return []
    
    async def save_message(self, user_id: int, message: str, is_user: bool = True) -> bool:
        """
        Сохранение сообщения в историю диалога
        
        Args:
            user_id: ID пользователя
            message: Текст сообщения
            is_user: Флаг, указывающий на то, что сообщение от пользователя
            
        Returns:
            bool: True если сообщение успешно сохранено
        """
        try:
            message_data = {
                "user_id": user_id,
                "message_text": message,
                "is_user": is_user,
                "created_at": datetime.now().isoformat()
            }
            
            response = supabase.table("conversations").insert(message_data).execute()
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении сообщения: {e}")
            return False
    
    async def generate_response(self, user_id: int, user_message: str) -> Optional[str]:
        """
        Генерация ответа на сообщение пользователя
        
        Args:
            user_id: ID пользователя
            user_message: Сообщение пользователя
            
        Returns:
            Optional[str]: Ответ AI-наставника или None в случае ошибки
        """
        try:
            # Получаем историю диалога
            conversation_history = await self.get_conversation_history(user_id)
            
            # Формируем список сообщений для OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})
            
            # Отправляем запрос к OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Получаем ответ
            ai_response = response.choices[0].message.content
            
            # Сохраняем сообщения в историю
            await self.save_message(user_id, user_message, is_user=True)
            await self.save_message(user_id, ai_response, is_user=False)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return None

# Создание экземпляра сервиса
openai_service = OpenAIService() 