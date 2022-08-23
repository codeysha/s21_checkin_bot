#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from telegram import ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import dal as data_layer
import mailer as mail

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


LOGIN, ACCESSCODE = range(2)


def help(update, context):
    update.message.reply_text('Help!')


def start(update, context):
    user_id = update.message.from_user.id
    print(user_id)
    user = data_layer.get_user_by_id(user_id)
    if user != 0:
        print(user)
        update.message.reply_text('Привет! ')
    else:
        update.message.reply_text('Укажи свою школьную почту:')
        return LOGIN


def login(update, context):
    user_email = update.message.text
    logger.info("entered user school email %s", user_email)
    role = data_layer.get_role_from_email(user_email)
    print(role)
    if role == 0:
        update.message.reply_text('Как будто бы вы не со школы. Если опечатались, попробуйте заново..')
        return start(update, context)
    # try to send email
    code = mail.generate_code(user_email)
    print('generated code: ', code)
    data_layer.save_access_code(code, user_email)
    mail.send(user_email, code, update.message.from_user.id)
    update.message.reply_text('check your email and enter an access code')
    return ACCESSCODE


def code(update, context):
    entered_code = update.message.text
    logger.info("user input next access code: %s", entered_code)
    code = data_layer.find_access_code(entered_code)
    update.message.reply_text('we will check your access code soon... please wait')
    if code != 0:
        update.message.reply_text('SUCCESS: code is correct! preparing to register you')
        user_id = update.message.from_user.id
        user_email = code['email']
        data_layer.save_user(user_id, user_email);
    else:
        update.message.reply_text('FAILURE: code is not correct or it is expired')
    return ConversationHandler.END


def echo(update, context):
    update.message.reply_text(update.message.from_user.id)
    update.message.reply_text(update.message.from_user.first_name)
    update.message.reply_text(update.message.from_user.last_name)
    update.message.reply_text(update.message.from_user.username)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться'
        ' Будет скучно - пиши.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    updater = Updater("5500494794:AAGFal5d3JwV2f6fJhUvEdEh5Y50krb9FME", use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("help", help))

    # Message handlers
    # dp.add_handler(MessageHandler(Filters.text, echo))
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LOGIN: [MessageHandler(Filters.text, login)],
            ACCESSCODE: [MessageHandler(Filters.text, code)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавляем обработчик разговоров `conv_handler`
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()