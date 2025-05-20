from telegram import Update
import logging
from ona.utils.handlers import InitialHandler, AwaitingInputHandler
from ona.core.fsm.handlers.registration_handler import RegistrationHandler, STATES as REGISTRATION_STATES
from ona.core.fsm.handlers.profiling_psychology_handler import ProfilingPsychologyHandler, STATE as PSYCHOLOGY_STATE

logger = logging.getLogger(__name__)

class StateRouter:
    """
    Класс для маршрутизации сообщений на основе FSM (Finite State Machine)
    """
    def __init__(self):
        """
        Инициализация маршрутизатора состояний
        """
        self.handlers = {}  # Словарь обработчиков для разных состояний
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """
        Регистрация обработчиков по умолчанию
        """
        self.register_handler("initial", InitialHandler())
        self.register_handler("awaiting_input", AwaitingInputHandler())
        
        # Регистрация обработчика для профилирования
        registration_handler = RegistrationHandler()
        for state in REGISTRATION_STATES.values():
            self.register_handler(state, registration_handler)
            
        # Регистрация обработчика для психологического профилирования
        psychology_handler = ProfilingPsychologyHandler()
        self.register_handler(PSYCHOLOGY_STATE, psychology_handler)
    
    def register_handler(self, state, handler):
        """
        Регистрация обработчика для определенного состояния
        
        Args:
            state: Состояние, для которого регистрируется обработчик
            handler: Обработчик для данного состояния
        """
        self.handlers[state] = handler
        logger.info(f"Зарегистрирован обработчик для состояния: {state}")
    
    async def route(self, update: Update):
        """
        Маршрутизация сообщения на основе текущего состояния пользователя
        
        Args:
            update: Обновление от Telegram
        """
        user_id = update.effective_user.id
        
        # Получение текущего состояния пользователя из базы данных
        # В будущем это должно быть заменено на реальную функцию получения состояния
        state = await self.get_user_state(user_id)
        
        logger.info(f"Маршрутизация сообщения для пользователя {user_id}, состояние: {state}")
        
        # Получение соответствующего обработчика
        handler = self.handlers.get(state)
        
        if handler:
            await handler.handle(update)
        else:
            # Обработка неизвестного состояния - используем обработчик начального состояния
            logger.warning(f"Не найден обработчик для состояния {state}, используем обработчик начального состояния")
            await self.handlers["initial"].handle(update)
    
    async def get_user_state(self, user_id):
        """
        Получение текущего состояния пользователя из базы данных
        
        Args:
            user_id: Идентификатор пользователя
            
        Returns:
            Текущее состояние пользователя или состояние по умолчанию
        """
        # Заглушка - в будущем будет заменена на получение состояния из базы данных
        return "initial"
    
    async def set_user_state(self, user_id, state):
        """
        Установка состояния пользователя в базе данных
        
        Args:
            user_id: Идентификатор пользователя
            state: Новое состояние
        """
        # Заглушка - в будущем будет заменена на сохранение состояния в базе данных
        logger.info(f"Установка состояния {state} для пользователя {user_id}")
        pass


# Создание экземпляра маршрутизатора состояний
state_router = StateRouter() 
