#!/usr/bin/env python3 from random import randint
# Токен ВК 52f77ec1453ecba7bcf5f23da2929237dc3bf0317965cf0c95b36cdce4883b0a68d2b798577b5b89b4165
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import time
import datetime
from icecream import ic





class BotAll:
    '''Родительский класс, в котором идёт подключение всех ботов к ВК'''
    def __init__(self,  main_token):
        self.vk_session = vk_api.VkApi(token=main_token)
        self.vk = self.vk_session.get_api()
        self.longpool = VkLongPoll(self.vk_session, preload_messages=True)

    def stick_send(self, user_id, number):
        '''Отправка стикеров'''
        self.vk.messages.send(user_id=user_id, sticker_id=number, random_id=0)

    def send_message(self, user_id, text, sticker_id= None, attachment= None):
        '''Отправка cообщений'''
        self.vk.messages.send(user_id=user_id, message=text, sticker_id=sticker_id, attachment= attachment, random_id=0)


    def run_bot(self):
        '''Запуск бесконечного мониторинга сообщений сообщества'''
        print('Работа бота началась!')

        for event in self.longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW:

                if event.to_me:
                # Здесь создаём переменные со всеми данными пользователя и сообщения.
                    self.msg = event.message.lower() # Сообщение переводим в нижний регистр
                    self.user_id = event.user_id # Запоминаем id пользователя
                    self.user = self.vk.users.get(user_id=self.user_id) # Получаем имя пользователя
                    self.fullname = self.user[0]['first_name'] + ' ' + self.user[0]['last_name']
                    ic(event)
                    if event.attachments: # Если в сообщении были вложения, то присваивем их
                        self.ivent_type = event.attachments
                    else:
                        self.ivent_type = None
                    self._client_message()


class BotClient(BotAll):
    '''Бот ответственный за работу с клиентом'''
    def __init__(self,main_token):
        super().__init__(main_token=main_token)
        self.details_of_the_Bank = '''Карта СБ
        4276 8640 2995 5943
        Саприна Мария Александровна'''

    def _market_request(self):
        self.send_message(user_id= self.user_id, sticker_id= 21313, text=self.details_of_the_Bank)



    def _client_message(self):
        '''Обработка сообщения пользователя'''
        now = datetime.datetime.now()
        print(self.ivent_type)
        print(now.strftime("%d-%m-%Y %H:%M"))
        if self.ivent_type and 'attach1_type' in self.ivent_type:
            self._processing_ivent()



    def _processing_ivent(self):
        '''Обработка вложений (кроме пересланнных сообщений)'''
        if self.ivent_type['attach1_type'] == 'market':
           product_number = 'market' + self.ivent_type['attach1']
           self._market_request()
           bot_piano_admin.market_mark(product_number=product_number, fullname =self.fullname,
           user_id=self.user_id)

        elif self.ivent_type['attach1_type'] == 'photo':
            photo_url = 'photo' + self.ivent_type['attach1']
            ic(photo_url)
            bot_piano_admin.forward_photo(photo_url=photo_url, fullname =self.fullname,
            user_id=self.user_id)




class BotAdmin(BotAll):
    '''Бот ответственный за работу с админами'''

    def __init__(self,main_token, admin_id, dialog_url):
        self.acess_key = '_52f77ec1453ecba7bcf5f23da2929237dc3bf0317965cf0c95b36cdce4883b0a68d2b798577b5b89b4165'
        self.admin_id = admin_id
        self.dialog_url = dialog_url
        super().__init__(main_token=main_token)


    def market_mark(self, product_number, fullname, user_id):
        '''Метод отправляет админам сообщества ссылку на диалог и сообщение пользователя о покупке нот'''

        print(product_number)

        text = f'Пользователь: {fullname} захотел ноты:\nСсылка на диалог: {self.dialog_url}{user_id}'
        self.send_message(user_id= self.admin_id, attachment=product_number, text= text)
        print(f'Пользователь: {fullname} захотел ноты')


    def forward_photo(self, photo_url, fullname, user_id):
        '''Метод отправляет админам сообщества ссылку на диалог и фотографию'''
        text = f'Пользователь: {fullname} отправил фотографию:\nСсылка на диалог: {self.dialog_url}{user_id}'
        photo_url = photo_url + self.acess_key
        ic(photo_url)

        self.send_message(user_id= self.admin_id, attachment=photo_url, text= text)
        print(f'Пользователь: {fullname} отпраил фото')



# TODO В следующей строчке id сообщества после "gim" и до "?" пока забивается руками.
# TODO Нужно будет найти способ автоматизировать это дело.
dialog_url = 'vk.com/gim139592783?sel='
main_token = 'd15d10710f19b31ed923df304110ba1637fe0cd6df17f0cf6fa65b635feef51c9cbee001d95e139db33e7'
admin_id = 46688565


bot_piano_client = BotClient(main_token=main_token)
bot_piano_admin = BotAdmin(main_token=main_token, admin_id=admin_id, dialog_url=dialog_url)

bot_piano_client.run_bot()
