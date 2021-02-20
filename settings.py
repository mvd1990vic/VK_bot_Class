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
    'market':{
        'first_step': 'step1',
        'steps':{
            'step1':{
                'text':'Запущен сценарий маркета',
                'failure_text': None,
                'handler': ['price', 'sheets'],
                'next_step': None
            }
        }
    }
}


#Конфиг sqlite Базы данных
DB_CONFIG = dict(
provider='sqlite',
    filename='bot.db',
    create_db=True,
)