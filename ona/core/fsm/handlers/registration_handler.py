from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from ..state_handler import StateHandler
from core.services.profile_service import profile_service
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

# Состояния для процесса регистрации и сбора натальных данных
STATES = {
    "START": "REGISTRATION_START",
    "BIRTH_DATE": "REGISTRATION_BIRTH_DATE",
    "BIRTH_TIME": "REGISTRATION_BIRTH_TIME",
    "BIRTH_PLACE": "REGISTRATION_BIRTH_PLACE",
    "AGE": "REGISTRATION_AGE",
    "COMPLETE": "REGISTRATION_COMPLETE",
    "PROFILING_NATAL": "PROFILING_NATAL"  # Добавлено для соответствия work-plan
}

class RegistrationHandler(StateHandler):
    """
    Обработчик для регистрации пользователя и сбора натальных данных
    """
    def __init__(self):
        # После завершения регистрации переходим к началу профайлинга личности
        super().__init__(next_state=STATES["COMPLETE"])
        self.user_data = {}
    
    async def handle(self, update: Update):
        """
        Маршрутизация сообщений в зависимости от текущего подсостояния регистрации
        
        Args:
            update: Обновление от Telegram
        """
        user_id = update.effective_user.id
        from utils.state_router import state_router
        
        # Определяем текущее подсостояние пользователя
        current_state = await state_router.get_user_state(user_id)
        logger.info(f"Обработка регистрации для пользователя {user_id}, состояние: {current_state}")
        
        # Маршрутизация по подсостояниям
        if current_state == STATES["START"]:
            await self.handle_start(update)
        elif current_state == STATES["BIRTH_DATE"]:
            await self.handle_birth_date(update)
        elif current_state == STATES["BIRTH_TIME"]:
            await self.handle_birth_time(update)
        elif current_state == STATES["BIRTH_PLACE"]:
            await self.handle_birth_place(update)
        elif current_state == STATES["AGE"]:
            await self.handle_age(update)
        elif current_state == STATES["PROFILING_NATAL"]:
            # Добавлено для соответствия work-plan, по сути дублирует START
            await self.handle_start(update)
        else:
            # Если состояние неизвестно, начинаем с начала
            await self.handle_start(update)
    
    async def handle_start(self, update: Update):
        """
        Начало процесса регистрации
        
        Args:
            update: Обновление от Telegram
        """
        user_id = update.effective_user.id
        from utils.state_router import state_router
        
        # Приветствие и запрос даты рождения (согласно work-plan)
        await update.message.reply_text(
            "Отлично! Давай начнем с первого этапа профайлинга. "
            "Для составления твоего персонального профиля мне нужна некоторая информация. "
            "Укажи, пожалуйста, свою дату рождения в формате ДД.ММ.ГГГГ (например, 15.03.1990)."
        )
        
        # Переход к сбору даты рождения
        await self.transition(user_id, state_router, STATES["BIRTH_DATE"])
    
    async def handle_birth_date(self, update: Update):
        """
        Обработка ввода даты рождения
        
        Args:
            update: Обновление от Telegram
        """
        user_id = update.effective_user.id
        from utils.state_router import state_router
        
        # Проверка формата даты рождения
        birth_date_text = update.message.text.strip()
        
        # Валидация даты с помощью регулярного выражения
        date_pattern = r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$'
        match = re.match(date_pattern, birth_date_text)
        
        if match:
            try:
                day, month, year = map(int, [match.group(1), match.group(2), match.group(3)])
                birth_date = datetime(year, month, day)
                
                # Проверка валидности даты
                if birth_date > datetime.now():
                    await update.message.reply_text(
                        "Дата рождения не может быть в будущем. Пожалуйста, введи корректную дату в формате ДД.ММ.ГГГГ."
                    )
                    return
                
                # Сохранение даты рождения
                self.user_data["birth_date"] = birth_date_text
                
                # Запрос времени рождения
                keyboard = ReplyKeyboardMarkup(
                    [["Я не знаю время рождения"]], 
                    resize_keyboard=True, 
                    one_time_keyboard=True
                )
                
                await update.message.reply_text(
                    "Спасибо! Теперь, пожалуйста, введи время рождения в формате ЧЧ:ММ (например, 14:30).\n"
                    "Если ты не знаешь точное время, нажми на кнопку ниже.",
                    reply_markup=keyboard
                )
                
                # Переход к сбору времени рождения
                await self.transition(user_id, state_router, STATES["BIRTH_TIME"])
            
            except ValueError:
                await update.message.reply_text(
                    "Пожалуйста, введи корректную дату в формате ДД.ММ.ГГГГ (например, 15.03.1990)."
                )
        else:
            await update.message.reply_text(
                "Неверный формат даты. Пожалуйста, введи дату в формате ДД.ММ.ГГГГ (например, 15.03.1990)."
            )
    
    async def handle_birth_time(self, update: Update):
        """
        Обработка ввода времени рождения
        
        Args:
            update: Обновление от Telegram
        """
        user_id = update.effective_user.id
        from utils.state_router import state_router
        
        birth_time_text = update.message.text.strip()
        
        # Обработка случая, когда пользователь не знает время рождения
        if birth_time_text == "Я не знаю время рождения":
            self.user_data["birth_time"] = "неизвестно"
            await update.message.reply_text(
                "Хорошо, это не проблема. Теперь, пожалуйста, введи место твоего рождения (город или населенный пункт).",
                reply_markup=ReplyKeyboardRemove()
            )
            await self.transition(user_id, state_router, STATES["BIRTH_PLACE"])
            return
        
        # Валидация времени с помощью регулярного выражения
        time_pattern = r'^(\d{1,2}):(\d{2})$'
        match = re.match(time_pattern, birth_time_text)
        
        if match:
            try:
                hour, minute = map(int, [match.group(1), match.group(2)])
                
                # Проверка валидности времени
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    # Сохранение времени рождения
                    self.user_data["birth_time"] = birth_time_text
                    
                    # Запрос места рождения
                    await update.message.reply_text(
                        "Спасибо! Теперь, пожалуйста, введи место твоего рождения (город или населенный пункт).",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    
                    # Переход к сбору места рождения
                    await self.transition(user_id, state_router, STATES["BIRTH_PLACE"])
                else:
                    await update.message.reply_text(
                        "Пожалуйста, введи корректное время в формате ЧЧ:ММ (например, 14:30)."
                    )
            except ValueError:
                await update.message.reply_text(
                    "Пожалуйста, введи корректное время в формате ЧЧ:ММ (например, 14:30)."
                )
        else:
            await update.message.reply_text(
                "Неверный формат времени. Пожалуйста, введи время в формате ЧЧ:ММ (например, 14:30)."
            )
    
    async def handle_birth_place(self, update: Update):
        """
        Обработка ввода места рождения
        
        Args:
            update: Обновление от Telegram
        """
        user_id = update.effective_user.id
        from utils.state_router import state_router
        
        birth_place = update.message.text.strip()
        
        # Простая валидация места рождения
        if len(birth_place) < 2:
            await update.message.reply_text(
                "Пожалуйста, введи корректное место рождения (город или населенный пункт)."
            )
            return
        
        # Сохранение места рождения
        self.user_data["birth_place"] = birth_place
        
        # Запрос возраста
        keyboard = [[str(i)] for i in range(18, 81, 10)]
        keyboard.append(["Другой возраст"])
        
        await update.message.reply_text(
            "Спасибо! И последний вопрос - сколько тебе лет? Ты можешь выбрать из предложенных вариантов или ввести свой возраст.",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        
        # Переход к сбору возраста
        await self.transition(user_id, state_router, STATES["AGE"])
    
    async def handle_age(self, update: Update):
        """
        Обработка ввода возраста
        
        Args:
            update: Обновление от Telegram
        """
        user_id = update.effective_user.id
        from utils.state_router import state_router
        
        age_text = update.message.text.strip()
        
        # Обработка выбора "Другой возраст"
        if age_text == "Другой возраст":
            await update.message.reply_text(
                "Пожалуйста, введи свой возраст числом.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        try:
            age = int(age_text)
            
            # Проверка валидности возраста
            if 1 <= age <= 120:
                # Сохранение возраста
                self.user_data["age"] = age
                
                # Сохранение данных пользователя
                await self.save_user_data(user_id)
                
                # Завершение регистрации
                await update.message.reply_text(
                    f"Отлично! Первый этап профайлинга завершен. Вот данные, которые я записала:\n\n"
                    f"📅 Дата рождения: {self.user_data.get('birth_date')}\n"
                    f"🕒 Время рождения: {self.user_data.get('birth_time')}\n"
                    f"📍 Место рождения: {self.user_data.get('birth_place')}\n"
                    f"👤 Возраст: {self.user_data.get('age')}\n\n"
                    f"Теперь мы можем перейти к следующему этапу профайлинга.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Продолжить профайлинг", callback_data="continue_profiling")]
                    ])
                )
                
                # Переход к завершению регистрации
                await self.transition(user_id, state_router, STATES["COMPLETE"])
            else:
                await update.message.reply_text(
                    "Пожалуйста, введи корректный возраст (от 1 до 120 лет)."
                )
        except ValueError:
            await update.message.reply_text(
                "Пожалуйста, введи возраст числом."
            )
    
    async def save_user_data(self, user_id):
        """
        Сохранение данных пользователя в базу данных
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с сохраненными данными
        """
        logger.info(f"Сохранение натальных данных для пользователя {user_id}: {self.user_data}")
        
        # Используем сервис профилей для сохранения данных
        try:
            await profile_service.save_natal_data(user_id, self.user_data)
        except Exception as e:
            logger.error(f"Ошибка при сохранении натальных данных: {e}")
        
        # Возвращаем копию данных и очищаем хранилище
        natal_data = self.user_data.copy()
        self.user_data = {}
        
        return natal_data 