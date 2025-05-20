"""
Машина состояний для управления диалогом
"""
from typing import Dict
from ona.core.fsm.state_handler import StateHandler
from core.fsm.handlers.subscription_handler import SubscriptionHandler
from core.fsm.handlers.chat_handler import ChatHandler
from core.fsm.handlers.recommendation_handler import RecommendationHandler

class StateMachine:
    def __init__(self):
        self.handlers: Dict[str, StateHandler] = {
            "SUBSCRIPTION": SubscriptionHandler(),
            "CHAT": ChatHandler(),
            "RECOMMENDATION": RecommendationHandler(),
        } 
