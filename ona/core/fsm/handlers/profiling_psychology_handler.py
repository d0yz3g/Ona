from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from ..state_handler import StateHandler
from core.models.psychology_questions import questions
from core.services.profile_service import profile_service
from core.services.openai_service import openai_service
import logging

logger = logging.getLogger(__name__)

# Состояние для психологического профилирования
STATE = "PROFILING_PSYCHOLOGY"

class ProfilingPsychologyHandler(StateHandler):
    """
    Обработчик для состояния психологического профайлинга
    """
    def __init__(self):
        # После завершения психологического профайлинга переходим к следующему этапу
        super().__init__(next_state="PROFILE_READY")
    
    async def handle(self, update: Update):
        """
        Маршрутизация сообщений в зависимости от типа обновления
        
        Args:
            update: Обновление от Telegram
        """
        user_id = update.effective_user.id
        
        # Получение прогресса пользователя в психологическом опроснике
        user_progress = await self.get_psychology_progress(user_id)
        
        # Если это callback_query (ответ на вопрос), обрабатываем его
        if update.callback_query:
            await self.process_answer(update.callback_query, user_progress)
            return
        
        # Если это текстовое сообщение или первый вопрос
        if user_progress is None or user_progress < len(questions):
            question_index = 0 if user_progress is None else user_progress
            await self.ask_question(update, question_index)
        else:
            # Если все вопросы заданы, генерируем психологический профиль
            await self.generate_profile(update)
    
    async def ask_question(self, update, question_index):
        """
        Отправка вопроса пользователю
        
        Args:
            update: Обновление от Telegram
            question_index: Индекс вопроса
        """
        question = questions[question_index]
        
        # Создание клавиатуры с вариантами ответов
        keyboard = []
        for option in question["options"]:
            callback_data = f"answer_{question_index}_{option['id']}"
            keyboard.append([InlineKeyboardButton(option["text"], callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправка вопроса
        message_text = f"Вопрос {question_index + 1}/{len(questions)}: {question['text']}"
        
        if update.callback_query:
            await update.callback_query.message.edit_text(message_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message_text, reply_markup=reply_markup)
    
    async def process_answer(self, callback_query, user_progress):
        """
        Обработка ответа на вопрос
        
        Args:
            callback_query: Callback запрос от кнопки
            user_progress: Текущий прогресс пользователя
        """
        # Разбор данных callback
        data = callback_query.data
        parts = data.split("_")
        
        if len(parts) != 3 or parts[0] != "answer":
            return
        
        question_index = int(parts[1])
        option_id = parts[2]
        
        # Получение вопроса и выбранного ответа
        question = questions[question_index]
        selected_option = next((opt for opt in question["options"] if opt["id"] == option_id), None)
        
        if not selected_option:
            logger.error(f"Не найден вариант ответа с ID {option_id} для вопроса {question_index}")
            return
        
        # Сохранение ответа
        user_id = callback_query.from_user.id
        await self.save_psychology_answer(user_id, question_index, option_id, selected_option["text"])
        
        # Обновление прогресса
        next_question_index = question_index + 1
        
        # Если есть следующий вопрос, переходим к нему
        if next_question_index < len(questions):
            await self.set_psychology_progress(user_id, next_question_index)
            
            # Создание нового Update объекта для отправки следующего вопроса
            update = Update(update_id=0, callback_query=callback_query)
            await self.ask_question(update, next_question_index)
        else:
            # Если вопросы закончились, генерируем профиль
            await self.set_psychology_progress(user_id, len(questions))
            await callback_query.message.edit_text(
                "Отлично! Ты ответила на все вопросы психологического опросника. "
                "Сейчас я анализирую твои ответы и формирую твой психологический профиль..."
            )
            
            # Создание нового Update объекта для генерации профиля
            update = Update(update_id=0, message=callback_query.message, effective_user=callback_query.from_user)
            await self.generate_profile(update)
    
    async def generate_profile(self, update):
        """
        Генерация психологического профиля пользователя на основе ответов с использованием OpenAI API
        
        Args:
            update: Обновление от Telegram
        """
        user_id = update.effective_user.id
        
        # Получение всех ответов пользователя
        answers = await self.get_psychology_answers(user_id)
        
        if not answers or len(answers) < len(questions):
            await update.message.reply_text("Для генерации психологического профиля нужно ответить на все вопросы.")
            return
        
        # Получение натальных данных пользователя
        natal_data = await profile_service.get_natal_data(user_id)
        
        # Объединение данных для генерации профиля
        user_data = {
            "birth_date": natal_data.get("birth_date") if natal_data else None,
            "birth_time": natal_data.get("birth_time") if natal_data else None,
            "birth_place": natal_data.get("birth_place") if natal_data else None,
            "age": natal_data.get("age") if natal_data else None,
            "psychology_answers": answers
        }
        
        # Отправка сообщения о начале генерации профиля
        await update.message.reply_text("Генерирую твой психологический профиль на основе ответов...")
        
        # Генерация профиля с помощью OpenAI API
        profile_text = await openai_service.generate_profile(user_data)
        
        # Сохранение сгенерированного профиля
        await self.save_psychology_profile(user_id, {"generated_text": profile_text})
        
        # Переход к следующему состоянию
        from utils.state_router import state_router
        await state_router.set_user_state(user_id, "PROFILE_READY")
        
        # Отправка результатов пользователю
        await update.message.reply_text(
            f"🧠 Твой психологический профиль готов!\n\n{profile_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Перейти к следующему этапу", callback_data="next_stage")]
            ])
        )
    
    async def get_psychology_progress(self, user_id):
        """
        Получение текущего прогресса пользователя в психологическом опроснике
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Индекс текущего вопроса или None, если пользователь еще не начал опросник
        """
        # Получение прогресса из базы данных
        try:
            profile = await profile_service.get_profile(user_id)
            if profile and "psychology_progress" in profile:
                return profile["psychology_progress"]
        except Exception as e:
            logger.error(f"Ошибка при получении прогресса психологического профилирования: {e}")
        
        return None
    
    async def set_psychology_progress(self, user_id, progress):
        """
        Установка текущего прогресса пользователя в психологическом опроснике
        
        Args:
            user_id: ID пользователя
            progress: Индекс текущего вопроса
        """
        try:
            await profile_service.update_profile_field(user_id, "psychology_progress", progress)
        except Exception as e:
            logger.error(f"Ошибка при обновлении прогресса психологического профилирования: {e}")
    
    async def save_psychology_answer(self, user_id, question_index, option_id, option_text):
        """
        Сохранение ответа пользователя на вопрос психологического опросника
        
        Args:
            user_id: ID пользователя
            question_index: Индекс вопроса
            option_id: ID выбранного варианта ответа
            option_text: Текст выбранного варианта ответа
        """
        try:
            # Получение текущих ответов
            profile = await profile_service.get_profile(user_id)
            psychology_answers = profile.get("psychology_answers", {}) if profile else {}
            
            # Добавление нового ответа
            psychology_answers[str(question_index)] = {
                "question_id": questions[question_index]["id"],
                "question_text": questions[question_index]["text"],
                "option_id": option_id,
                "option_text": option_text
            }
            
            # Сохранение обновленных ответов
            await profile_service.update_profile_field(user_id, "psychology_answers", psychology_answers)
        except Exception as e:
            logger.error(f"Ошибка при сохранении ответа на вопрос психологического профилирования: {e}")
    
    async def get_psychology_answers(self, user_id):
        """
        Получение всех ответов пользователя на вопросы психологического опросника
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с ответами пользователя
        """
        try:
            profile = await profile_service.get_profile(user_id)
            if profile and "psychology_answers" in profile:
                return profile["psychology_answers"]
        except Exception as e:
            logger.error(f"Ошибка при получении ответов психологического профилирования: {e}")
        
        return {}
    
    async def save_psychology_profile(self, user_id, profile):
        """
        Сохранение психологического профиля пользователя
        
        Args:
            user_id: ID пользователя
            profile: Психологический профиль
        """
        try:
            await profile_service.update_profile_field(user_id, "psychology_profile", profile)
        except Exception as e:
            logger.error(f"Ошибка при сохранении психологического профиля: {e}") 