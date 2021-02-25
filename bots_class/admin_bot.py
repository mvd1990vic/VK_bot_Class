#!/usr/local/bin/python
from icecream import ic
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotEventType

from bots_class.parrent_bot import Bot
from private_settings import ADMIN_TOKEN, ADMIN_GROUP_ID, PEOPLE_ADMIN_ID, DIALOG_URL


class AdminBot(Bot):
    """
    Бот для работы с админами сообщества. Отправляет сообщения о покупке нот другими пользователями. Так же хочется
    реализовать кнопки для отправки нот клиентам и работу с базой данных о покупках и клиентах
    """

    def __init__(self, main_token, group_id, admin_id, dialog_url):
        super().__init__(main_token=main_token, group_id=group_id)
        self.dialog_url = dialog_url
        self.admin_id = admin_id

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



    def message_from_user(self, event):
        """Отправка сообщения от пользователя админам"""
        text_user = event.text
        fullname, user_id = self.get_name_user(event)

        if text_user:
            text = (f'Пользователь: {fullname} написал сообщение:\n {text_user}\n\
                    Ссылка на диалог: {self.dialog_url}{user_id}')

            self.send_message(user_id=self.admin_id, text=text)


    def product_from_user(self):
        """Отправка товаров от пользователя"""
        pass

    def photo_from_user(self, event):
        """Отправка фото от пользователя"""
        photo_url = ('photo' + str(event.attachments[0]['photo']['owner_id']) + '_' +
                    str(event.attachments[0]['photo']['id']) + '_' + str(event.attachments[0]['photo']['access_key']))
        fullname, user_id = self.get_name_user(event)
        text_user = event.text
        text = f'Пользователь: {fullname} отправил фотографию:\nСсылка на диалог: {self.dialog_url}{user_id}\n'


        self.send_message(user_id=self.admin_id, attachment=photo_url, text=text)




admin_bot = AdminBot(main_token=ADMIN_TOKEN, group_id=ADMIN_GROUP_ID, admin_id=PEOPLE_ADMIN_ID, dialog_url=DIALOG_URL)