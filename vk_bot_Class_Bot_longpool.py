#!/usr/bin/env python3 from random import randint
# Токен ВК 52f77ec1453ecba7bcf5f23da2929237dc3bf0317965cf0c95b36cdce4883b0a68d2b798577b5b89b4165
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import time
import datetime
from icecream import ic





class BotAll:
    '''Родительский класс, в котором идёт подключение всех ботов к ВК'''
    def __init__(self,  main_token, group_id):
        self.group_id = group_id
        self.vk_session = vk_api.VkApi(token=main_token)
        self.vk = self.vk_session.get_api()
        self.longpool = VkBotLongPoll(self.vk_session, self.group_id)

    def stick_send(self, user_id, number):
        '''Отправка стикеров'''
        self.vk.messages.send(user_id=user_id, sticker_id=number, random_id=0)

    def send_message(self, user_id, text, sticker_id=None, attachment=None):
        '''Отправка cообщений'''
        self.vk.messages.send(user_id=user_id, message=text, sticker_id=sticker_id, attachment= attachment, random_id=0)


    def run_bot(self):
        '''Запуск бесконечного мониторинга сообщений сообщества'''
        print('Работа бота началась!')

        for event in self.longpool.listen():
            self.on_event(self, event)


    def on_event(self, pre_event, event):

        if event.type == VkBotEventType.MESSAGE_NEW:
            # ic(event)
            # Здесь создаём переменные со всеми данными пользователя и сообщения.
            self.event_all = event.message
            self.msg = event.message.text.lower()  # Сообщение переводим в нижний регистр
            self.peer_id = event.message.peer_id  # Запоминаем peer пользователя
            self.user = self.vk.users.get(user_id=self.peer_id)  # Получаем имя пользователя
            self.fullname = self.user[0]['first_name'] + ' ' + self.user[0]['last_name']

            if event.message.attachments:  # Если в сообщении были вложения, то присваивем их
                ic(event.message)
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
        self.send_message(user_id= self.peer_id, sticker_id= 21313, text=self.details_of_the_Bank)



    def client_message(self):
        '''Обработка сообщения пользователя'''
        now = datetime.datetime.now()
        print(now.strftime("%d-%m-%Y %H:%M"))
        if self.event_type:
            self._processing_ivent()



    def _processing_ivent(self):
        '''Обработка вложений (кроме пересланнных сообщений)'''

        ic(self.event_type[0])
        if 'market' in self.event_type[0]:

            product_number = ('market' + str(self.event_type[0]['market']['owner_id']) + '_' +
                              str(self.event_type[0]['market']['id']))

            self._market_request()
            bot_piano_admin.market_mark(product_number=product_number, fullname =self.fullname,
            user_id=self.peer_id)

        elif 'photo' in self.event_type[0]:
            photo_url = ('photo' + str(self.event_type[0]['photo']['owner_id']) + '_' +
                        str(self.event_type[0]['photo']['id']) + '_' + str(self.event_type[0]['photo']['access_key']))

            ic(photo_url)
            bot_piano_admin.forward_photo(photo_url=photo_url, fullname =self.fullname,
            user_id=self.peer_id)




class BotAdmin(BotAll):
    '''Бот ответственный за работу с админами'''

    def __init__(self,main_token, admin_id, dialog_url, group_id ):
        self.group_id = group_id
        self.admin_id = admin_id
        self.dialog_url = dialog_url
        super().__init__(main_token=main_token, group_id=group_id)


    def market_mark(self, product_number, fullname, user_id):
        '''Метод отправляет админам сообщества ссылку на диалог и сообщение пользователя о покупке нот'''

        print(product_number)

        text = f'Пользователь: {fullname} захотел ноты:\nСсылка на диалог: {self.dialog_url}{user_id}'
        self.send_message(user_id= self.admin_id, attachment=product_number, text= text)
        print(f'Пользователь: {fullname} захотел ноты')


    def forward_photo(self, photo_url, fullname, user_id):
        '''Метод отправляет админам сообщества ссылку на диалог и фотографию'''
        text = f'Пользователь: {fullname} отправил фотографию:\nСсылка на диалог: {self.dialog_url}{user_id}'
        ic(photo_url)

        self.send_message(user_id= self.admin_id, attachment=photo_url, text= text)
        print(f'Пользователь: {fullname} отпраил фото')



# TODO В следующей строчке id сообщества после "gim" и до "?" пока забивается руками.
# TODO Нужно будет найти способ автоматизировать это дело.
dialog_url = 'vk.com/gim139592783?sel='
main_token = '13676fe2496f6fd4abde7e5fa93a654f4201be630d4c047530f5cd9b1194cd062167f6175cf79a44eeaa3'
group_id = 139592783
admin_id = 46688565


bot_piano_client = BotClient(main_token=main_token, group_id=group_id)
bot_piano_admin = BotAdmin(main_token=main_token, admin_id=admin_id, dialog_url=dialog_url, group_id=group_id)

bot_piano_client.run_bot()
