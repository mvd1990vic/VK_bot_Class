"""
Handler - обработчики событий разных сценариев.

"""


def price(event, context):
    if 'price' not in context:
        context['price'] = 0
    pricer = int(int(event.attachments[0]['market']['price']['amount']) / 100)
    context['price'] += pricer


def sheets(event, context):
    context['sheets'] = []
    sheet = event.attachments[0]['market']['title']
    context['sheets'].append(sheet)
