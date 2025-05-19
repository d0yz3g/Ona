from telegram import Update
import logging

logger = logging.getLogger(__name__)

class StateHandler:
    """
    Базовый класс для обработчиков состояний FSM
    """
    def __init__(self, next_state=None):
        """
        Инициализация обработчика состояния
        
        Args:
            next_state: Следующее состояние, в которое нужно перейти после обработки
        """
        self.next_state = next_state
    
    async def handle(self, update: Update):
        """
        Метод для обработки сообщения в текущем состоянии
        
        Args:
            update: Обновление от Telegram
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def transition(self, user_id, state_router, state=None):
        """
        Переход в следующее состояние
        
        Args:
            user_id: ID пользователя
            state_router: Объект маршрутизатора состояний
            state: Состояние, в которое нужно перейти (если не задано, используется self.next_state)
        """
        target_state = state or self.next_state
        if target_state:
            await state_router.set_user_state(user_id, target_state)
            logger.info(f"Пользователь {user_id} перешел в состояние {target_state}") 