INTENTS = [
    {
        'name': 'Приветствие',
        'tokens': ('здравствуйте', 'привет', 'хай', 'здорова'),
        'scenario': None,
        'answer': 'И тебе добрый день!!! \n'
                  'Если хочешь приобрести ноты, то воспользуйся товарами в моём сообществе:\n'
                  'https://vk.com/market-69097195\n'
                  'P.S: Если потребуется ответ от Марии, она прочитает и ответит :)\n'
                  'С уважением, **БОТ СООБЩЕСТВА**.'
    },
    {
        'name': 'Вызов сценария маркета',
        'tokens': ('market', 'маркет'),
        'scenario': 'market',
        'answer': None
    },

]

SCENARIOS = {
    'market': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'admin_method': 'market_mark',
                'message_to_admin': 'Пользователь {name_user} захотел ноты {sheet}',
                'sticker_id': 21313,
                'text': '''
Доброго времени суток!! Для оплаты можно воспользоваться моими реквизитами:

Карта СБ
4276 8640 2995 5943
Саприна Мария Александровна

Эти ноты стоят {price} ₽. Вы так же можете продолжить выбор товаров в каталоге маркета по ссылке:
https://vk.com/market-69097195

После оплаты напишите об этом сюда, ну а лучше скиньте скрин квитанции :)
С уважением, **БОТ СООБЩЕСТВА**.''',
                'failure_text': None,
                'handler': ['price', 'sheets', 'sheets_id'],
                'next_step': 'step2'
            },
            'step2': {
                'admin_method': 'market_mark',
                'message_to_admin': 'Пользователь {name_user} захотел ноты {sheet}',
                'sticker_id': None,
                'text': 'Отлично эти ноты мы тоже зафиксировали. Итого к оплате поучается: {price} ₽\nС уважением, **БОТ СООБЩЕСТВА**.',
                'failure_text': None,
                'handler': ['price', 'sheets','sheets_id'],
                'next_step': 'step2'
            }
        }
    }
}

INTENTS_ADMINS = [
    {
        'name': 'Запрос открытых запросов на покупку',
        'tokens': ['кто'],
        'scenario': None,
        'answer': 'В данный момент эти люди хотят приобрести ноты:\n',
        'handler': 'user_line'
    },
    {
        'name': 'Покупка нот',
        'tokens': ['отправь'],
        'scenario': None,
        'answer': 'Ноты отправлены.',
        'handler': 'send_notes'
    },
    {
        'name': 'Удаление клиента',
        'tokens': ['удали'],
        'scenario': None,
        'answer': 'Заявка на ноты удалена.',
        'handler': 'delete_client'
    },
    {
        'name': 'Очистка статуса заказов',
        'tokens': ['очисти'],
        'scenario': None,
        'answer': 'Заказы почищены.',
        'handler': 'clear_state'
    },
]


# Не отправляемые сообщения
NO_SEND_MESSAGES = [
'''Здравствуйте!
Меня заинтересовал этот товар.''',
]

# Конфиг sqlite Базы данных
DB_CONFIG = dict(
    provider='sqlite',
    filename='bot.db',
    create_db=True,
)


DEFAULT_ANSWER_ADMIN = 'Если хочешь узнать, кто хочет купить ноты: набери "кто"\n' \
                       'Если хочешь отравить ноты, то набери "отпраавь" и его порядковый номер'

PURCASHE_MESSAGE = ['оплатил', 'оплатили', 'оплатила']
