#!/usr/local/bin/python
import threading

from icecream import ic
from vk_api import vk_api
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

    def run(self):
        """
        Запуск бесконечного мониторинга событий сообщества.
        Если состоялось событие, то вызываем метод on_event из дочернего класса client_bot.
        Так же вызов on_event обвёрнут в try/except что бы работа бота не прикращалась.
        """
        print('Работа бота началась:')

        for event in self.longpool.listen():
            #try:
                self.on_event(event)
            #except Exception as exc:
             #  print('Ошибка в обработке: ', exc )

    def send_message(self, user_id, text, sticker_id=None, attachment=None):
        """Отправка сообщений от бота"""
        self.vk.messages.send(user_id=user_id, message=text, attachment=attachment, random_id=0)
        # Отправка стикера
        if sticker_id:
            self.vk.messages.send(user_id=user_id, sticker_id=sticker_id, random_id=0)


    def get_name_user(self, event):
        user_id = event.peer_id
        user_name = self.vk.users.get(user_id=user_id)
        fullname = user_name[0]['first_name'] + ' ' + user_name[0]['last_name']
        return fullname, user_id