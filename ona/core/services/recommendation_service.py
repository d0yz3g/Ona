"""
Сервис для работы с персонализированными рекомендациями
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime
from core.services.openai_service import openai_service
from core.services.profile_service import profile_service
from core.db.supabase_client import supabase

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Сервис для работы с персонализированными рекомендациями
    """
    def __init__(self):
        """
        Инициализация сервиса рекомендаций
        """
        self.openai_service = openai_service
        self.profile_service = profile_service
    
    async def _check_profile_exists(self, telegram_id: int) -> bool:
        """
        Проверка существования профиля пользователя
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            bool: True если профиль существует
        """
        try:
            profile = await self.profile_service.get_user_profile(telegram_id)
            return bool(profile)
        except Exception as e:
            logger.error(f"Ошибка при проверке профиля: {e}")
            return False
    
    async def generate_daily_recommendation(self, telegram_id: int) -> Optional[str]:
        """
        Генерирует ежедневную персонализированную рекомендацию
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Optional[str]: Текст рекомендации или None в случае ошибки
        """
        try:
            # Проверяем наличие профиля
            if not await self._check_profile_exists(telegram_id):
                return "Для получения рекомендаций необходимо сначала пройти профайлинг."
            
            # Получаем профиль пользователя
            profile = await self.profile_service.get_user_profile(telegram_id)
            
            # Формируем системный промпт
            system_prompt = """
            Ты эксперт по психологии и персональному развитию. Твоя задача - создать короткую,
            но эффективную рекомендацию на день, основываясь на психологическом профиле человека.
            Рекомендация должна быть конкретной, практичной и легко выполнимой.
            """
            
            # Формируем пользовательский промпт
            user_prompt = f"""
            На основе следующего психологического профиля создай одну конкретную рекомендацию на сегодня:
            
            {profile}
            
            Рекомендация должна быть:
            1. Краткой (не более 3-4 предложений)
            2. Конкретной (что именно нужно сделать)
            3. Реалистичной (возможной выполнить за день)
            4. Направленной на улучшение эмоционального благополучия
            
            Не используй общие фразы вроде "постарайся быть счастливее".
            Дай точный совет, который можно применить сегодня.
            """
            
            # Генерируем рекомендацию через OpenAI
            response = await self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            recommendation = response.choices[0].message.content
            
            # Сохраняем рекомендацию в базу данных
            await self.save_recommendation(telegram_id, recommendation)
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ежедневной рекомендации: {e}")
            return None
    
    async def generate_practice(self, telegram_id: int, practice_type: str = "mindfulness") -> Optional[str]:
        """
        Генерирует персонализированную практику определенного типа
        
        Args:
            telegram_id: Telegram ID пользователя
            practice_type: Тип практики (mindfulness/stress/sleep/energy)
            
        Returns:
            Optional[str]: Текст практики или None в случае ошибки
        """
        try:
            # Проверяем наличие профиля
            if not await self._check_profile_exists(telegram_id):
                return "Для получения практик необходимо сначала пройти профайлинг."
            
            # Получаем профиль пользователя
            profile = await self.profile_service.get_user_profile(telegram_id)
            
            # Маппинг типов практик к промптам
            practice_prompts = {
                "mindfulness": "короткую практику осознанности (3-5 минут)",
                "stress": "практику для снижения стресса (5-7 минут)",
                "sleep": "практику для улучшения сна (5-10 минут)",
                "energy": "практику для повышения энергии (2-3 минуты)"
            }
            
            if practice_type not in practice_prompts:
                return "Указанный тип практики не поддерживается."
            
            # Формируем системный промпт
            system_prompt = """
            Ты эксперт по медитации и практикам осознанности. Твоя задача - создать
            персонализированную практику, которая будет полезна конкретному человеку
            на основе его психологического профиля.
            """
            
            # Формируем пользовательский промпт
            user_prompt = f"""
            На основе следующего психологического профиля создай {practice_prompts[practice_type]}:
            
            {profile}
            
            Практика должна быть:
            1. Простой и понятной
            2. Легкой для выполнения
            3. Соответствующей указанной длительности
            4. Учитывающей особенности личности
            
            Опиши практику пошагово, используя простой язык.
            """
            
            # Генерируем практику через OpenAI
            response = await self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            practice = response.choices[0].message.content
            
            # Сохраняем практику в базу данных
            await self.save_practice(telegram_id, practice_type, practice)
            
            return practice
            
        except Exception as e:
            logger.error(f"Ошибка при генерации практики: {e}")
            return None
    
    async def save_recommendation(self, telegram_id: int, recommendation: str) -> bool:
        """
        Сохранение рекомендации в базу данных
        
        Args:
            telegram_id: Telegram ID пользователя
            recommendation: Текст рекомендации
            
        Returns:
            bool: True если рекомендация успешно сохранена
        """
        try:
            # Получаем ID пользователя
            user_result = supabase.table("users").select("id").eq("telegram_id", telegram_id).execute()
            
            if not user_result.data:
                logger.error(f"Пользователь с telegram_id {telegram_id} не найден")
                return False
            
            user_id = user_result.data[0]["id"]
            
            # Сохраняем рекомендацию
            recommendation_data = {
                "user_id": user_id,
                "type": "daily",
                "content": recommendation,
                "created_at": datetime.now().isoformat()
            }
            
            response = supabase.table("recommendations").insert(recommendation_data).execute()
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении рекомендации: {e}")
            return False
    
    async def save_practice(self, telegram_id: int, practice_type: str, practice: str) -> bool:
        """
        Сохранение практики в базу данных
        
        Args:
            telegram_id: Telegram ID пользователя
            practice_type: Тип практики
            practice: Текст практики
            
        Returns:
            bool: True если практика успешно сохранена
        """
        try:
            # Получаем ID пользователя
            user_result = supabase.table("users").select("id").eq("telegram_id", telegram_id).execute()
            
            if not user_result.data:
                logger.error(f"Пользователь с telegram_id {telegram_id} не найден")
                return False
            
            user_id = user_result.data[0]["id"]
            
            # Сохраняем практику
            practice_data = {
                "user_id": user_id,
                "type": practice_type,
                "content": practice,
                "created_at": datetime.now().isoformat()
            }
            
            response = supabase.table("practices").insert(practice_data).execute()
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении практики: {e}")
            return False

# Создание экземпляра сервиса
recommendation_service = RecommendationService() 