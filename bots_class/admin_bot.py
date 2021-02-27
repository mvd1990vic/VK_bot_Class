#!/usr/local/bin/python
import re

from icecream import ic
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotEventType

from bots_class import handlers
from bots_class.parrent_bot import Bot, EventContentHandler
from databases.user_db import AdminState, UserState
from private_settings import ADMIN_TOKEN, ADMIN_GROUP_ID, PEOPLE_ADMIN_ID, DIALOG_URL
from settings import NO_SEND_MESSAGES, INTENTS_ADMINS, DEFAULT_ANSWER_ADMIN


class AdminBot(Bot, EventContentHandler):
    """
    Бот для работы с админами сообщества. Отправляет сообщения о покупке нот другими пользователями. Так же хочется
    реализовать кнопки для отправки нот клиентам и работу с базой данных о покупках и клиентах
    """

    def __init__(self, main_token, group_id, admin_id, dialog_url):
        super().__init__(main_token=main_token, group_id=group_id)
        self.dialog_url = dialog_url
        self.admin_id = admin_id
        self.user_state = UserState

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
        print('Админ написал сообщение')
        ic(event.message)
        user_id = event.message.peer_id
        state = AdminState.get(user_id=str(user_id))  # получение состояния пользователя в сценарии.
        self._message_handler(event=event.message, state_user=state)

    def _message_handler(self, event, state_user):
        """
        Метод запускает обработку сообщения по INTENTS (запросам/намерениям)
        @param event: Немного усечёный event (без блока с type)
        @param state_user: Статус админа в словаре.
        @return:
        """
        user_id = event.peer_id
        text_to_send = None
        sticker_id = None


            # search intent
        for intent in INTENTS_ADMINS:

            if any (token in event.text.lower() for token in intent['tokens']):
                # run intent
                if intent['answer']:
                    text_to_send = intent['answer'] + self.intent_event(event=event, intent=intent)
                # Пока в этой ветке сценарии не реалтзованны
                #else:
                    #text_to_send = self.start_scenario(user_id,intent['scenario'])
                break
            else:
                text_to_send = DEFAULT_ANSWER_ADMIN
        if text_to_send:
            self.send_message(user_id=user_id, text=text_to_send, sticker_id=sticker_id)

    def intent_event(self, event, intent):
        """Создание ответа для админа"""
        if intent['handler'] == 'user_line':
            all_user_line = []
            for client in self.user_state.select(lambda x: x.id ):
                id = client.id
                fullname = self.handler_content(user_id=client.user_id, get_content='fullname', vk=self.vk)
                price = client.context['price']
                sheets = ', '.join(client.context['sheets'])
                user_line = f'{id} {fullname} {sheets} {price} руб. '

                all_user_line.append(user_line)
            all_user_line = '\n'.join(all_user_line)

            return all_user_line
        elif intent['handler'] == 'send_notes':
            id_client = re.findall(r'\d+', event.text)
            id_client = ''.join(id_client)
            state = UserState.get(id=str(id_client))
            state.delete()
            return ''

        elif intent['handler'] == 'delete_client':
            id_client = re.findall(r'\d+', event.text)
            id_client = ''.join(id_client)
            state = UserState.get(id=str(id_client))
            state.delete()
            return ''
        elif intent['handler'] == 'clear_state':

            state = UserState.get()
            state.delete()
            return ''



    def message_from_user(self, event):
        """Отправка сообщения от пользователя админам"""
        text_user = event.text
        fullname = self.handler_content(get_content='fullname', event=event, vk=self.vk)
        user_id = self.handler_content(event=event, get_content='user_id')

        if text_user and text_user not in NO_SEND_MESSAGES:
            text = (f'Пользователь: [id{user_id}|{fullname}] написал сообщение:\n {text_user}\n'
                    f'Ссылка на диалог: {self.dialog_url}{user_id}')

            self.send_message(user_id=self.admin_id, text=text)


    def product_from_user(self, event):
        """Отправка товаров от пользователя"""
        product_name = self.handler_content(event=event,get_content='product_name')
        product_number = self.handler_content(event=event,get_content='product_number')
        fullname = self.handler_content(event=event,get_content='fullname', vk=self.vk )
        user_id = self.handler_content(event=event,get_content='user_id')

        text = f'Пользователь: [id{user_id}|{fullname}] захотел ноты:\n ' \
               f'***  {product_name}  ***\n' \
               f'Ссылка на диалог: {self.dialog_url}{user_id}\n'
        self.send_message(user_id=self.admin_id, text=text)
        # Этот метод отправляет экземпляр маркета. пока посчитали такой вариант неудобным
        # self.send_message(user_id=self.admin_id, attachment=product_number, text=text)

    def photo_from_user(self, event):
        """Отправка фото от пользователя"""
        photo_number = self.handler_content(event=event,get_content='photo_number')

        fullname = self.handler_content(event=event, get_content='fullname', vk=self.vk)
        user_id = self.handler_content(event=event, get_content='user_id')
        text = f'Пользователь: [id{user_id}|{fullname}] отправил фотографию:\n' \
               f'Ссылка на диалог: {self.dialog_url}{user_id}'


        self.send_message(user_id=self.admin_id, attachment=photo_number, text=text)





admin_bot = AdminBot(main_token=ADMIN_TOKEN, group_id=ADMIN_GROUP_ID, admin_id=PEOPLE_ADMIN_ID, dialog_url=DIALOG_URL)