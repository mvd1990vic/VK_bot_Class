#!/usr/local/bin/python
from icecream import ic
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotEventType

from bots_class.parrent_bot import Bot
from databases.user_db import UserState
from settings import INTENTS


class ClientBot(Bot):
    """
    Бот для работы с клиентами сообщества. Отправляет клиентам реквизиты, переправляет их сообщения боту-админу, по
    возможности отправляет им ноты, подсчитивает сколько надо заптатить за ноты и т.д.
    """

    def __init__(self, main_token, group_id):
        super().__init__(main_token=main_token, group_id=group_id)

    @db_session
    def on_event(self, event):
        """
        Проверяет событие на предмет нового сообщения.
        Если событие является сообщением, то именуются все важные параметры и передаются в метод обработки сообщений.
        @param event: событие упавшее из ВК.
        @return:
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
           return
        print('Пользователь написал сообщение')
        ic(event.message)
        user_id = event.message.peer_id
        state = UserState.get(user_id=str(user_id)) # получение состояния пользователя в сценарии.
        self._message_handler(event=event.message, state_user=state)


    def _message_handler(self, event, state_user):
        """
        Метод запускает обработку сообщения по INTENTS (запросам/намерениям)
        @param event: Немного усечёный event (без блока с type)
        @param state_user: Статус клиента в словаре.
        @return:
        """
        ic(state_user)
        if state_user:
            # continue scenario
            self.continue_scenario(event=event, state_user=state_user)
        else:
            # search intent
            text = event.text
            if event.attachments:
                attachments = event.attachments[0]
            else:
                attachments = ''
            ic(attachments)
            for intent in INTENTS:
            # Find token in INTENTS
                if any (token in text.lower() for token in intent['tokens']) or \
                   any (token in attachments for token in intent['tokens'] ):
                    pass





    def continue_scenario(self, event, state_user):
        """Продолжение сценария, если в таблице действующих сценариев присутствует id полльзователя"""
        pass