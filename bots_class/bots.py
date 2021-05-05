#!/usr/local/bin/python
import csv
import time
import re

from bots_class.parrent_bot import EventContentHandler
from databases.user_db import AdminState, AllUser
from private_settings import ADMIN_TOKEN, ADMIN_GROUP_ID, PEOPLE_ADMIN_ID, DIALOG_URL
from settings import NO_SEND_MESSAGES, INTENTS_ADMINS, DEFAULT_ANSWER_ADMIN, PURCASHE_MESSAGE

from icecream import ic
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotEventType

from bots_class import handlers
from bots_class.parrent_bot import Bot
from databases.user_db import UserState
from private_settings import MAIN_TOKEN, GROUP_ID
from settings import INTENTS, SCENARIOS


class ClientBot(Bot, EventContentHandler):
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
        state = UserState.get(user_id=str(user_id))  # получение состояния пользователя в сценарии.
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
        sticker_id = None
        state_all_users = AllUser.get(user_id=str(user_id))
        if state_all_users:
            pass
        else:
            user_name = self.handler_content(get_content='fullname', vk=self.vk, user_id=user_id)
            AllUser(user_id=str(user_id), user_name=user_name)

        if event.attachments:
            attachments = event.attachments[0]
        else:
            attachments = ''
        if state_user:
            text = event.text
            text_to_send, sticker_id, admin_method, message_to_admin = \
                self.continue_scenario(event=event, state_user=state_user)
        else:
            # search intent
            text = event.text

            for intent in INTENTS:
                # Find token in INTENTS
                if any(token in attachments for token in intent['tokens']) or \
                        any(token in text.lower() for token in intent['tokens']) and attachments == '':
                    if intent['answer']:
                        text_to_send = intent['answer']
                        print('Запущен ответ')

                    else:
                        text_to_send, sticker_id, admin_method, message_to_admin = \
                            self.start_scenario(event=event, scenario_name=intent['scenario'])
                        print('Запущен сценарий')
                    break
        admin_bot.message_from_user(event)
        if 'photo' in attachments:
            admin_bot.photo_from_user(event)
        if text_to_send or sticker_id:
            self.send_message(user_id=user_id, text=text_to_send, sticker_id=sticker_id)

    def start_scenario(self, event, scenario_name):
        """Запуск обработки сценария"""
        context = {}
        scenario = SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        for handler in step['handler']:
            handler = getattr(handlers, handler)
            handler(event=event, context=context)

        user_id = event.peer_id

        text_to_send = (step['text'].format(**context))
        sticker_id = step['sticker_id']
        admin_method = step['admin_method']
        message_to_admin = step['message_to_admin']
        new_id = None
        for i in range(1, 50):
            find_id = UserState.get(id=str(i))
            if find_id:
                pass
            else:
                new_id = i
                break

        UserState(id=new_id, user_id=str(user_id), scenario_name=scenario_name,
                  step_name=first_step, context=context)

        admin_bot.product_from_user(event)
        return text_to_send, sticker_id, admin_method, message_to_admin

    def continue_scenario(self, event, state_user):
        """Продолжение сценария, если в таблице действующих сценариев присутствует id пользователя"""
        steps = SCENARIOS[state_user.scenario_name]['steps']
        step = steps[state_user.step_name]
        if state_user.scenario_name == 'market':
            admin_method, message_to_admin, sticker_id, text_to_send = self.continue_scenario_market(event, state_user,
                                                                                                     step, steps)
        else:
            text_to_send = None
            sticker_id = None
            admin_method = None
            message_to_admin = None
        return text_to_send, sticker_id, admin_method, message_to_admin

    def upload_files(self, state):
        """
        Подготовка к отправки файлов
        @param state: строка из базы данных пользователей
        @return:
        """
        sheets = dict(zip(state.context['sheets'], state.context['sheets_id']))
        for sheet_name, sheet_id in sheets.items():
            self.send_files(sheet_id, sheet_name, state)
            time.sleep(2)

        self.send_message(user_id=state.user_id, text='Приятного разучивания!!!')

    def send_files(self, sheet_id, sheet_name, state):
        with open('databases/sheets_info.csv', 'r', newline='', encoding='utf-8') as csv_file:
            csv_data = csv.DictReader(csv_file)
            for row in csv_data:
                ic(row['sheets_id'], sheet_id)
                if int(row['sheets_id']) == (sheet_id):
                    sheets_file = f'files/{row["sheets_file"]}'
                    with open(sheets_file) as fi:
                        print(fi)
                    file = self.upload.document_message(doc=sheets_file, title=row['sheets_file'], tags='sheet',
                                                        peer_id=state.user_id)

                    name_file = f'doc{file["doc"]["owner_id"]}_{file["doc"]["id"]}'
                    self.send_message(user_id=state.user_id, attachment=name_file, text=None)

    def continue_scenario_market(self, event, state_user, step, steps):
        if event.attachments:
            attachments = event.attachments[0]
        else:
            attachments = ''
        if 'market' in attachments:
            admin_bot.product_from_user(event)
            for handler in step['handler']:
                handler = getattr(handlers, handler)
                handler(event=event, context=state_user.context)
            next_step = steps[step['next_step']]
            text_to_send = (next_step['text'].format(**state_user.context))
            sticker_id = next_step['sticker_id']
            admin_method = next_step['admin_method']
            message_to_admin = next_step['message_to_admin']
            if next_step['next_step']:
                state_user.step_name = step['next_step']
            else:
                state_user.delete()
                text_to_send = 'Конец сценария'
        elif 'photo' in attachments or 'doc' in attachments or event.text.lower()  in PURCASHE_MESSAGE:
            time_message = event.date
            local_time = time.gmtime(time_message)
            local_hour = local_time.tm_hour
            ic(local_hour)
            if 21 - 7 <= local_hour or local_hour < 8 - 7:
                text_to_send = 'Скорее всего вы оплатили ноты, но у нас сейчас немного поздно и увидим оплату мы ' \
                               'только когда проснёмся, но как только увидим, так сразу отправим вам ноты\nС уважением, **БОТ СООБЩЕСТВА**.'
                sticker_id = 13
            else:
                text_to_send = None
                sticker_id = None
            admin_method = None
            message_to_admin = None
        else:
            text_to_send = None
            sticker_id = None
            admin_method = None
            message_to_admin = None

        return admin_method, message_to_admin, sticker_id, text_to_send


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

            if any(token in event.text.lower() for token in intent['tokens']):
                # run intent
                if intent['answer']:
                    text_to_send = intent['answer'] + self.intent_event(event=event, intent=intent)
                # Пока в этой ветке сценарии не реалтзованны
                # else:
                # text_to_send = self.start_scenario(user_id,intent['scenario'])
                break
            else:
                text_to_send = DEFAULT_ANSWER_ADMIN
        if text_to_send:
            self.send_message(user_id=user_id, text=text_to_send, sticker_id=sticker_id)

    def intent_event(self, event, intent):
        """Создание ответа для админа"""
        if intent['handler'] == 'user_line':
            all_user_line = []
            for client in self.user_state.select(lambda x: x.id):
                id = client.id
                fullname = self.handler_content(user_id=client.user_id, get_content='fullname', vk=self.vk)
                price = client.context['price']
                sheets_lens = len(client.context['sheets'])
                sheets = ', \n'.join(client.context['sheets'])
                user_line = f'{id} {fullname}\n {sheets} Итого: {sheets_lens} на {price} руб.\n\n'

                all_user_line.append(user_line)
            all_user_line = '\n'.join(all_user_line)

            return all_user_line
        elif intent['handler'] == 'send_notes':
            id_client = re.findall(r'\d+', event.text)
            id_client = ''.join(id_client)
            state = UserState.get(id=str(id_client))
            client_bot.upload_files(state=state)
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
        product_name = self.handler_content(event=event, get_content='product_name')
        product_number = self.handler_content(event=event, get_content='product_number')
        fullname = self.handler_content(event=event, get_content='fullname', vk=self.vk)
        user_id = self.handler_content(event=event, get_content='user_id')

        text = f'Пользователь: [id{user_id}|{fullname}] захотел ноты:\n ' \
               f'***  {product_name}  ***\n' \
               f'Ссылка на диалог: {self.dialog_url}{user_id}\n'
        self.send_message(user_id=self.admin_id, text=text)
        # Этот метод отправляет экземпляр маркета. пока посчитали такой вариант неудобным
        # self.send_message(user_id=self.admin_id, attachment=product_number, text=text)

    def photo_from_user(self, event):
        """Отправка фото от пользователя"""
        photo_number = self.handler_content(event=event, get_content='photo_number')

        fullname = self.handler_content(event=event, get_content='fullname', vk=self.vk)
        user_id = self.handler_content(event=event, get_content='user_id')
        text = f'Пользователь: [id{user_id}|{fullname}] отправил фотографию:\n' \
               f'Ссылка на диалог: {self.dialog_url}{user_id}'

        self.send_message(user_id=self.admin_id, attachment=photo_number, text=text)


admin_bot = AdminBot(main_token=ADMIN_TOKEN, group_id=ADMIN_GROUP_ID, admin_id=PEOPLE_ADMIN_ID, dialog_url=DIALOG_URL)

client_bot = ClientBot(main_token=MAIN_TOKEN, group_id=GROUP_ID)
