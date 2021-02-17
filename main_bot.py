#!/usr/local/bin/python
from bots_class.admin_bot import AdminBot
from bots_class.client_bot import ClientBot
from settings import MAIN_TOKEN, GROUP_ID

client_bot = ClientBot(main_token=MAIN_TOKEN, group_id=GROUP_ID)
admin_bot = AdminBot()

if __name__ == '__main__':
    client_bot.run()
