# coding: utf-8
from functools import wraps
import os
import re

from loguru import logger
import requests
from telegram import ChatAction
from telegram.ext import BaseFilter, Filters, CommandHandler, MessageHandler


def call_function(name, input_data, **query):
    openfaas_gateway = os.getenv('gateway_hostname', 'gateway')
    return requests.get(
        'http://{gateway}:8080/function/{function}'.format(gateway=openfaas_gateway, function=name),
        data=input_data,
        params=query,
    )


def send_action(action):
    '''Decorator to send action before actually sending message'''

    def decorator(func):

        @wraps(func)
        def decorated(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=action)
            return func(update, context, *args, **kwargs)

        return decorated

    return decorator


class MofishTextFilter(BaseFilter):
    '''Detect if given text message indicates the user wants to touch the fish'''

    top_patterns = [
        re.compile(r'.*(?<![不别])想+(早点|快点)*(下班|回家|睡觉|补休|摸鱼|返屋企)(?![吗么]).*', re.M),
        re.compile(r'.*(?<=[好很])(困|想睡觉|眼瞓|累)(?![吗么]).*', re.M),
        re.compile(r'.*(?<=[不])想+(上班|加班|醒目|敬业)(?![吗么]).*', re.M),
    ]


    def filter(self, message):
        text = message.text
        if not text:
            return False

        for p in self.top_patterns:
            if p.findall(text):
                return True

        return False


@send_action(ChatAction.TYPING)
def reply_mofish_text(update, context):
    update.message.reply_text('虽然我很赞同你的想法，但很遗憾，我现在还没有时间观念。摸了', quote=True)


@send_action(ChatAction.TYPING)
def classify_picture(update, context):
    message = update.effective_message.reply_to_message
    if message and message.photo:
        photo = message.photo[0].get_file()
        try:
            result = call_function('inception', photo.file_path)
        except Exception:
            logger.exception('Failed to classify {}', photo.file_path)
            message.reply_text('抱歉，我现在不在状态，摸了')
        else:
            if result.status_code == 200:
                results = [
                    i['name'] for i in sorted(result.json(), key=lambda x: x['score'], reverse=True)
                ]
                message.reply_text(
                    'It might be one of these: \n{}'.format('\n'.join([
                        '- {}'.format(i) for i in set(results)
                    ])),
                    quote=True
                )
            else:
                message.reply_text('抱歉，我现在不在状态，摸了')
                logger.exception('Classify error code {}', result.status_code)
    else:
        update.effective_chat.send_message('只能对图片使用')


handlers = [
    MessageHandler(Filters.text & MofishTextFilter(), reply_mofish_text),
    CommandHandler('what', classify_picture),
]

