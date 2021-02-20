"""
Handler - обработчики событий разных сценариев.

"""

def price(event, context):
    if not 'price' in context:
        context['price'] = 0
    price = int(int(event.attachments[0]['market']['price']['amount']) / 100)
    context['price'] += price

def sheets(event, context):
    context['sheets'] = []
    sheet = event.attachments[0]['market']['title']
    context['sheets'].append(sheet)