#!/usr/local/bin/python
from icecream import ic
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


class Bot:
    """
    Основная часть бота в ней проходит подключение к вк и определение метода отправки сообщения, т.к. это возможно
    и для клиента и для админа.
    """

    def __init__(self, main_token, group_id):  # Инициализация бота
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
            try:
                self.on_event(event)
            except Exception as exc:
                print('Ошибка в обработке: ', exc )


