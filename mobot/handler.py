# coding: utf-8
import re
from io import open
import json

from loguru import logger
from telegram import Bot, Update


with open('/var/openfaas/secrets/mobot-telegram-bot-token') as rf:
    bot = Bot(token=rf.read())


top_patterns = [
    re.compile(r'.*(?<![不别])想+(早点|快点)*(下班|回家|睡觉|补休|摸鱼|返屋企)(?![吗么]).*', re.M),
    re.compile(r'.*(?<=[好很])(困|想睡觉|眼瞓|累)(?![吗么]).*', re.M),
]
group_patterns = []


def filter_text(text):
    '''Either match one of the top patterns, or
    match two of the patterns in a single group.
    '''
    for p in top_patterns:
        if p.findall(text):
            return True

    for patterns1, patterns2 in group_patterns:
        matched = 0
        for p in patterns1:
            if p.findall(text):
                matched = 1
                break
        if matched == 1:
            for p in patterns2:
                if p.findall(text):
                    return True

    return False


def handle(event, context):
    try:
        update = Update.de_json(json.loads(event.body), bot)
    except:
        return {'statusCode': 400}

    if not update:
        return {'statusCode': 400}

    if update.message:
        message = update.message
        if filter_text(message.text):
            message.reply_text('虽然我很赞同你的想法，但很遗憾，我现在还没有时间观念。摸了', quote=True)

    return {
        "statusCode": 200,
    }

