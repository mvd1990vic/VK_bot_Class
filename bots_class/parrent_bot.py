#!/usr/local/bin/python
import threading

from icecream import ic
from vk_api import vk_api, VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


class Bot(threading.Thread):
    """
    Основная часть бота в ней проходит подключение к вк и определение метода отправки сообщения, т.к. это возможно
    и для клиента и для админа.
    """

    def __init__(self, main_token, group_id, *args, **kwargs):  # Инициализация бота
        super(Bot, self).__init__(*args, **kwargs)
        self.group_id = group_id  # id группы передаётся из файла settings.py
        self.vk_session = vk_api.VkApi(token=main_token)  # Запуск ВК сессии при помощи токена API
        self.vk = self.vk_session.get_api()
        self.longpool = VkBotLongPoll(self.vk_session, self.group_id)
        self.upload = VkUpload(self.vk)

    def run(self):
        """
        Запуск бесконечного мониторинга событий сообщества.
        Если состоялось событие, то вызываем метод on_event из дочернего класса client_bot.
        Так же вызов on_event обвёрнут в try/except что бы работа бота не прикращалась.
        """
        print('Работа бота началась:')

        for event in self.longpool.listen():
            try:
                self.on_event(event)
            except Exception as exc:
                print('Ошибка в обработке: ', exc )

    def send_message(self, user_id, text, sticker_id=None, attachment=None):
        """Отправка сообщений от бота"""

        if isinstance(user_id, list):
            for id in user_id:
                self.vk.messages.send(user_id=id, message=text, attachment=attachment, random_id=0)
                # Отправка стикера
                if sticker_id:
                    self.vk.messages.send(user_id=id, sticker_id=sticker_id, random_id=0)
        else:
            self.vk.messages.send(user_id=user_id, message=text, attachment=attachment, random_id=0)
            # Отправка стикера
            if sticker_id:
                self.vk.messages.send(user_id=user_id, sticker_id=sticker_id, random_id=0)




class EventContentHandler:
    """
    Класс обработки содержимого события для облегчения чтения основных ботов.
    """
    def handler_content(self, get_content, event=None, vk=None, user_id=None):
        """
        @param event: Передаём событие целиком
        @param get_content: по запросу переходим по методу
        @param vk: для некоторых запросов нужны параметры ВК сессии

        @return: возвращение обработанных данных
        """

        if get_content == 'fullname':
            return self.get_name_user(event=event,vk=vk, user_id=user_id)
        elif get_content == 'user_id':
            return self.get_user_id(event=event)
        elif get_content == 'product_number':
            return self.get_product_number(event=event)
        elif get_content == 'product_name':
            return self.get_product_name(event=event)
        elif get_content == 'photo_url':
            return self.get_photo_url(event=event)
        elif get_content == 'photo_number':
            return self.get_photo_number(event=event)

    def get_photo_url(self,event):
        photo_url= event.attachments[0]['photo']['sizes'][3]['url']
        return photo_url


    def get_name_user(self,vk, event=None, user_id=None):
        if user_id:
            user_id = user_id

        else:
            user_id = event.peer_id



        user_name = vk.users.get(user_id=user_id)
        fullname = user_name[0]['first_name'] + ' ' + user_name[0]['last_name']
        return fullname

    def get_user_id(self, event):
        user_id = event.peer_id
        return user_id

    def get_product_number(self,event):
        product_number = ('market' + str(event.attachments[0]['market']['owner_id']) + '_' +
                          str(event.attachments[0]['market']['id']))
        return product_number

    def get_photo_number(self,event):
        photo_number = ('photo' + str(event.attachments[0]['photo']['owner_id']) + '_' +
                     str(event.attachments[0]['photo']['id']) + '_' + str(event.attachments[0]['photo']['access_key']))
        return photo_number

    def get_product_name(self,event):
        product_name = event.attachments[0]['market']['title']
        return product_name