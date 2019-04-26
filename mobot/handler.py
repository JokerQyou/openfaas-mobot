# coding: utf-8
from io import open
import json

from loguru import logger
from telegram import Bot, Update


with open('/var/openfaas/secrets/mobot-telegram-bot-token') as rf:
    bot = Bot(token=rf.read())


def handle(event, context):
    update = Update.de_json(json.loads(event.body), bot)
    if not update:
        return {'statusCode': 400}

    if update.message:
        message = update.message
        if message.text and '摸鱼' in message.text:
            message.reply_text('复读模式：' + message.text, quote=True)

    return {
        "statusCode": 200,
    }

