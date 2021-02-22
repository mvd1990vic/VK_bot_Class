INTENTS = [
    {
        'name': 'Приветствие',
        'tokens': ('здравствуйте', 'привет', 'хай', 'здорова'),
        'scenario': None,
        'answer': 'И тебе добрый день!!! \n'
                  'Если хочешь приобрести ноты, то воспользуйся товарами в моём сообществе:\n'
                  'https://vk.com/market-69097195'
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
                'sticker_id': 21313,
                'text': '''Доброго времени суток для оплаты можно воспользоваться моими реквизитами:
        
        Карта СБ
        4276 8640 2995 5943
        Саприна Мария Александровна
        
        Эти ноты стоят {price} ₽. Вы так же можете продолжить выбор товаров в каталоге маркета
        После оплаты напишите об этом сюда, ну а лучше скиньте скрин квитанции.''',
                'failure_text': None,
                'handler': ['price', 'sheets'],
                'next_step': 'step2'
            },
            'step2': {
                'sticker_id': None,
                'text': 'Ещё один тест Шаг 2',
                'failure_text': None,
                'handler': ['price', 'sheets'],
                'next_step': 'step2'
            }
        }
    }
}

# Конфиг sqlite Базы данных
DB_CONFIG = dict(
    provider='sqlite',
    filename='bot.db',
    create_db=True,
)
