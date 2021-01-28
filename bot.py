#!/usr/bin/env python3
from random import randint

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import time
import datetime

id_admins = [46688565, 63883576]
# Основной бот
main_token = '66c40be8dfa8292d2846e8a4168703fd680b77dd1aa768500ad90502fb8d5fa35f28fde82108d6c091448'
# тестовый бот
# main_token = 'd15d10710f19b31ed923df304110ba1637fe0cd6df17f0cf6fa65b635feef51c9cbee001d95e139db33e7'

vk_session = vk_api.VkApi(token=main_token)
vk = vk_session.get_api()
longpool = VkLongPoll(vk_session)
details_of_the_Bank = '''
карта СБ

4276 8640 2995 5943
Саприна Мария Александровна'''

welcome_words = ['привет', 'ghbdtn', 'хай', 'здравствуйте', 'ghbdt']

bank_details = ['реквизиты']


def send_stick(id, number):
    vk.messages.send(user_id=id, sticker_id=number, random_id=0)
    print('Бот отправил стикер')


def send_photo(id, url):
    vk.messages.send(user_id=id, attachment=url, random_id=0)
    print('Бот отправил фото')


def sender(id, text):
    vk.messages.send(user_id=id, message=text, random_id=0)
    print(f'Ответ бота: {text}')


def send_admin(id, user_message, fullname):
    text = f'Там {fullname} написал:\n{user_message} \nСсылка на диалог: vk.com/gim69097195?sel={id}'
    for id_admin in id_admins:
        vk.messages.send(user_id=id_admin, message=text, random_id=0)



def send_admin_photo(id, url, fullname):
    text = f'Там {fullname} прислал фото:\nСсылка на диалог: vk.com/gim69097195?sel={id}'
    photo_id = f'photo{url}'
    for id_admin in id_admins:
        vk.messages.send(user_id=id_admin,message=text, attachment=photo_id, random_id=0)


def send_admin_market(id, url, fullname):
    text = f'Там {fullname} захотел ноты:\nСсылка на диалог: vk.com/gim69097195?sel={id}'
    market_id = f'market{url}'
    for id_admin in id_admins:
        vk.messages.send(user_id=id_admin, message=text, attachment=market_id , random_id=0)



print('Работа бота началась')

def run():
    try:
        for event in longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:


                    msg = event.message.lower()
                    id = event.user_id
                    user = vk.users.get(user_id=id)

                    fullname = user[0]['first_name'] + ' ' + user[0]['last_name']
                    print(fullname + ':')

                    print(f'Сообщение от пользователя: {msg}')

                    if msg in welcome_words:
                        sender(id, 'И тебе привет')
                        send_stick(id, 30)
                    elif event.attachments and 'attach1_type' in event.attachments and event.attachments['attach1_type'] == 'market':
                        market = event.attachments['attach1']
                        send_admin_market(id=id, url=market, fullname=fullname)
                        answer = f'Здравствуйте!\n {details_of_the_Bank}'
                        search_repeat = vk.messages.search(q=answer, count=1, peer_id=id)


                        if search_repeat ['count'] == 0:
                            sender(id, answer)
                            send_stick(id, 21313)
                        else:
                            message_time = search_repeat['items'][0]['date']
                            actual_time = time.time() - 172800
                            print(message_time)
                            print(actual_time)

                            if message_time > actual_time:
                                pass
                            else:
                                sender(id, answer)
                                send_stick(id, 21313)
                    elif event.attachments and 'attach1_type' in event.attachments and event.attachments['attach1_type'] == 'photo':
                        photo = event.attachments['attach1']
                        send_admin_photo(id=id, url=photo, fullname=fullname)
                        print('Прислали фото')


                    else:
                        send_admin(id=id, user_message=msg, fullname=fullname)
                        print('Боту нечего ответить')
    except:
        run()



run()
