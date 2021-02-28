#!/usr/local/bin/python

from bots_class.bots import client_bot, admin_bot


def main():
    client_bot.start()
    admin_bot.start()


if __name__ == '__main__':
    main()


