# coding: utf-8
'''
This is the entrance module for OpenFaas.
'''
from io import open
import json

from loguru import logger
from telegram import Bot, Update
from telegram.ext import Dispatcher

from .bot import handlers


with open('/var/openfaas/secrets/mobot-telegram-bot-token') as rf:
    bot = Bot(token=rf.read())
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)


# Register handlers
for handler in handlers:
    dispatcher.add_handler(handler)


def handle(event, context):
    try:
        update = Update.de_json(json.loads(event.body), bot)
    except:
        return {'statusCode': 400}
    else:
        dispatcher.process_update(update)
        return {'statusCode': 200}


