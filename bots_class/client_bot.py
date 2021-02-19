#!/usr/local/bin/python
from icecream import ic
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotEventType

from bots_class.parrent_bot import Bot
from databases.user_db import UserState
from settings import INTENTS, SCENARIOS


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
        user_id = event.peer_id
        text_to_send = None
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
            for intent in INTENTS:
            # Find token in INTENTS
                if any (token in attachments for token in intent['tokens'] ) or \
                   any (token in text.lower() for token in intent['tokens']) and attachments == '':
                    if intent['answer']:
                        text_to_send = intent['answer']
                        print('Запущен ответ')

                    else:
                        text_to_send = self.start_scenario(event=event, scenario_name=intent['scenario'])
                        print('Запущен сценарий')
                    break
        ic(text_to_send)
        self.send_message(user_id=user_id, text=text_to_send)

    def start_scenario(self, event, scenario_name):
        """Запуск обработки сценария"""
        # TODO Нужно подумать как сделать рефакторинг добавления значений в СЛВАРЬ context, что бы работало для разных сценариев
        context = {}
        context['sheets'] = []
        context['price'] = 0
        user_id = event.peer_id
        price = int(int(event.attachments[0]['market']['price']['amount'])/100)
        sheet = event.attachments[0]['market']['title']
        ic(price)
        scenario = SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']

        context['sheets'].append(sheet)
        context['price'] += price


        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context=context)
        return text_to_send




    def continue_scenario(self, event, state_user):
        """Продолжение сценария, если в таблице действующих сценариев присутствует id полльзователя"""
        pass