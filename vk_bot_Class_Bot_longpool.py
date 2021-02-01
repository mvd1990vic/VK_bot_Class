#!/usr/bin/env python3
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import datetime
from icecream import ic
# В файле confidential_data содержатся ID Админа сообщества, токенсообщества и ID группы
from confidential_Data import *



class BotAll:
    '''Родительский класс, в котором идёт подключение всех ботов к ВК'''

    def __init__(self, main_token, group_id):
        self.group_id = group_id
        self.vk_session = vk_api.VkApi(token=main_token)
        self.vk = self.vk_session.get_api()
        self.longpool = VkBotLongPoll(self.vk_session, self.group_id)

    def send_message(self, user_id, text, sticker_id=None, attachment=None):
        '''Отправка cообщений'''
        self.vk.messages.send(user_id=user_id, message=text, sticker_id=sticker_id, attachment=attachment, random_id=0)

    def run_bot(self):
        '''Запуск бесконечного мониторинга сообщений сообщества'''
        print('Работа бота началась!')

        for event in self.longpool.listen():
            self.on_event(self, event)

    def on_event(self, pre_event, event):

        if event.type == VkBotEventType.MESSAGE_NEW:
            ic(event)
            # Здесь создаём переменные со всеми данными пользователя и сообщения.
            self.msg = event.message.text.lower()  # Сообщение переводим в нижний регистр
            self.peer_id = event.message.peer_id  # Запоминаем peer пользователя
            self.user = self.vk.users.get(user_id=self.peer_id)  # Получаем имя пользователя
            self.fullname = self.user[0]['first_name'] + ' ' + self.user[0]['last_name']

            if event.message.attachments:  # Если в сообщении были вложения, то присваивем их
                # ic(event.message)
                self.event_type = event.message.attachments

            else:
                self.event_type = None
            self.client_message()


class BotClient(BotAll):
    '''Бот ответственный за работу с клиентом'''

    def __init__(self, main_token, group_id):
        super().__init__(main_token=main_token, group_id=group_id)
        self.details_of_the_Bank = '''Карта СБ
        4276 8640 2995 5943
        Саприна Мария Александровна'''

    def _market_request(self):
        self.send_message(user_id=self.peer_id, sticker_id=21313, text=self.details_of_the_Bank)

    def client_message(self):
        '''Обработка сообщения пользователя'''
        now = datetime.datetime.now()
        print(now.strftime("%d-%m-%Y %H:%M"))
        if self.event_type:
            self._processing_ivent()
        else:
            bot_piano_admin.processing_message(fullname=self.fullname, user_id=self.peer_id)





    def _processing_ivent(self):
        '''Обработка вложений (кроме пересланнных сообщений)'''

        ic(self.event_type[0])
        if 'market' in self.event_type[0]:

            product_number = ('market' + str(self.event_type[0]['market']['owner_id']) + '_' +
                              str(self.event_type[0]['market']['id']))

            self._market_request()
            bot_piano_admin.market_mark(product_number=product_number, fullname=self.fullname,
                                        user_id=self.peer_id)

        elif 'photo' in self.event_type[0]:
            photo_url = ('photo' + str(self.event_type[0]['photo']['owner_id']) + '_' +
                         str(self.event_type[0]['photo']['id']) + '_' + str(self.event_type[0]['photo']['access_key']))

            bot_piano_admin.forward_photo(photo_url=photo_url, fullname=self.fullname,
                                          user_id=self.peer_id)




class BotAdmin(BotAll):
    '''Бот ответственный за работу с админами'''

    def __init__(self, main_token, admin_id, dialog_url, group_id):
        self.group_id = group_id
        self.admin_id = admin_id
        self.dialog_url = dialog_url
        super().__init__(main_token=main_token, group_id=group_id)

    def processing_message(self, fullname, user_id):
        '''Обработка текстовых сообщений'''
        text = (f'Пользователь: {fullname} написал сообщение:\n {bot_piano_client.msg}\n\
        Ссылка на диалог: {self.dialog_url}{user_id}')


        self.send_message(user_id=self.admin_id, text=text)
        print(f'{bot_piano_client.msg}')


    def market_mark(self, product_number, fullname, user_id):
        '''Метод отправляет админам сообщества ссылку на диалог и сообщение пользователя о покупке нот'''

        print(product_number)

        text = f'Пользователь: {fullname} захотел ноты:\nСсылка на диалог: {self.dialog_url}{user_id}\n' \
               f'И написал: {bot_piano_client.msg}'
        self.send_message(user_id=self.admin_id, attachment=product_number, text=text)
        print(f'Пользователь: {fullname} захотел ноты')

    def forward_photo(self, photo_url, fullname, user_id):
        '''Метод отправляет админам сообщества ссылку на диалог и фотографию'''
        text = f'Пользователь: {fullname} отправил фотографию:\nСсылка на диалог: {self.dialog_url}{user_id}\n' \
               f'И написал: {bot_piano_client.msg}'

        self.send_message(user_id=self.admin_id, attachment=photo_url, text=text)
        print(f'Пользователь: {fullname} отпраил фото')


# TODO В следующей строчке id сообщества после "gim" и до "?" пока забивается руками.
# TODO Нужно будет найти способ автоматизировать это дело.
dialog_url = 'vk.com/gim139592783?sel='
# Здесь можно подключить Токен, Id группы и Id Админа/админов
# main_token =
# group_id =
# people_admin_id =

bot_piano_client = BotClient(main_token=main_token, group_id=group_id)
bot_piano_admin = BotAdmin(main_token=main_token, admin_id=people_admin_id, dialog_url=dialog_url, group_id=group_id)

bot_piano_client.run_bot()
