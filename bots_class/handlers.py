"""
Handler - обработчики событий разных сценариев и интентов.

"""


def price(event, context):
    if 'price' not in context:
        context['price'] = 0
    pricer = int((int(event.attachments[0]['market']['price']['amount']) / 100)/2) #TODO Убрать 2 после распродажи
    context['price'] += pricer


def sheets(event, context):
    if 'sheets' not in context:
        context['sheets'] = []
    sheet = event.attachments[0]['market']['title']
    context['sheets'].append(sheet)

def sheets_id(event, context):
    if 'sheets_id' not in context:
        context['sheets_id'] = []
    sheets_id = event.attachments[0]['market']['id']
    context['sheets_id'].append(sheets_id)

