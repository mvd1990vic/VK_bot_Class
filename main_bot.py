#!/usr/local/bin/python
from bots_class.admin_bot import admin_bot
from bots_class.client_bot import client_bot






def main():
    client_bot.start()
    admin_bot.start()


if __name__ == '__main__':
    main()


