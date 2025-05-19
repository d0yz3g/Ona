import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProfileService:
    """
    Сервис для работы с профилями пользователей
    """
    def __init__(self, db_client=None):
        """
        Инициализация сервиса профилей
        
        Args:
            db_client: Клиент для работы с базой данных
        """
        self.db_client = db_client
    
    async def get_profile(self, user_id):
        """
        Получение профиля пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Профиль пользователя или None, если профиль не найден
        """
        if self.db_client:
            return await self.db_client.get_profile(user_id)
        else:
            logger.warning(f"DB клиент не инициализирован. Невозможно получить профиль для {user_id}")
            return None
    
    async def save_natal_data(self, user_id, natal_data):
        """
        Сохранение натальных данных пользователя
        
        Args:
            user_id: ID пользователя
            natal_data: Натальные данные (дата, время и место рождения, возраст)
            
        Returns:
            Результат операции
        """
        if not self.db_client:
            logger.warning(f"DB клиент не инициализирован. Невозможно сохранить данные для {user_id}")
            return False
        
        try:
            # Получаем текущий профиль, если он существует
            profile = await self.get_profile(user_id)
            
            # Подготавливаем данные для сохранения
            natal_profile_data = {
                "user_id": user_id,
                "birth_date": natal_data.get("birth_date"),
                "birth_time": natal_data.get("birth_time"),
                "birth_place": natal_data.get("birth_place"),
                "age": natal_data.get("age"),
                "updated_at": datetime.now().isoformat()
            }
            
            if profile:
                # Если профиль существует, обновляем его
                return await self.db_client.update_profile(user_id, natal_profile_data)
            else:
                # Если профиль не существует, создаем новый
                natal_profile_data["created_at"] = datetime.now().isoformat()
                return await self.db_client.create_profile(natal_profile_data)
        
        except Exception as e:
            logger.error(f"Ошибка при сохранении натальных данных для {user_id}: {e}")
            return False
    
    async def update_profile_field(self, user_id, field_name, field_value):
        """
        Обновление отдельного поля в профиле пользователя
        
        Args:
            user_id: ID пользователя
            field_name: Имя поля для обновления
            field_value: Новое значение поля
            
        Returns:
            Результат операции
        """
        if not self.db_client:
            logger.warning(f"DB клиент не инициализирован. Невозможно обновить поле {field_name} для {user_id}")
            return False
        
        try:
            # Получаем текущий профиль
            profile = await self.get_profile(user_id)
            
            if not profile:
                # Если профиль не существует, создаем новый с указанным полем
                new_profile_data = {
                    "user_id": user_id,
                    field_name: field_value,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                return await self.db_client.create_profile(new_profile_data)
            else:
                # Если профиль существует, обновляем указанное поле
                update_data = {
                    field_name: field_value,
                    "updated_at": datetime.now().isoformat()
                }
                return await self.db_client.update_profile(user_id, update_data)
        
        except Exception as e:
            logger.error(f"Ошибка при обновлении поля {field_name} для {user_id}: {e}")
            return False
    
    async def get_natal_data(self, user_id):
        """
        Получение натальных данных пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Натальные данные пользователя или None, если данные не найдены
        """
        profile = await self.get_profile(user_id)
        
        if not profile:
            return None
        
        return {
            "birth_date": profile.get("birth_date"),
            "birth_time": profile.get("birth_time"),
            "birth_place": profile.get("birth_place"),
            "age": profile.get("age")
        }
    
    async def is_natal_data_complete(self, user_id):
        """
        Проверка, заполнены ли натальные данные пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True, если натальные данные заполнены, иначе False
        """
        natal_data = await self.get_natal_data(user_id)
        
        if not natal_data:
            return False
        
        # Проверяем, что все необходимые поля заполнены (кроме времени рождения, которое может быть "неизвестно")
        required_fields = ["birth_date", "birth_place", "age"]
        for field in required_fields:
            if not natal_data.get(field):
                return False
        
        return True


# Создание экземпляра сервиса профилей
profile_service = ProfileService() 