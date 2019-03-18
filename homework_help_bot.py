#Refer to echobot2: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
import logging
import sqlite3

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging to handle uncaught exceptions
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

token = '837770119:AAEmP97SuF0moJezC0jipSHz5Uy-CXqNNoI'

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Welcome to sgHomeworkHelp!")

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('/help was entered as a command!\nWhat do you need help with?')

def ask(update, context):
    """Send a message when the command /ask is issued."""
    update.message.reply_text("/ask was entered as a command!\nWhat's your question?")

def ask_text(update, context):
    """Send a message when user asks a question (text format)."""
    update.message.reply_text(f"Your question is: {update.message.text}\nIt is awaiting reply!")

def register_user(update, context):
    """Send a message and request for user's contact (and location) when the command /register is issued."""
    update.message.reply_text("/register was entered as a command!")

    # location_keyboard_btn = telegram.KeyboardButton(text="send_location", request_location=True)
    contact_keyboard_btn = telegram.KeyboardButton(text="send_contact", request_contact=True)

    register_keyboard = [[ contact_keyboard_btn ]]
    reply_markup = telegram.ReplyKeyboardMarkup(register_keyboard)

    update.message.reply_text("Would you mind sharing your location and contact with me?", reply_markup=reply_markup)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    print('Program started!')

    updater = Updater(token=token, use_context=True)
    print('Bot is created!')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    print('Dispatcher is created!')

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    print('Start handler is created and added to dispatcher!')
    dp.add_handler(CommandHandler('help', help))
    print('Help handler is created and added to dispatcher!')
    dp.add_handler(CommandHandler('ask', ask))
    print('Ask handler is created and added to dispatcher!')
    dp.add_handler(CommandHandler('register', register_user))
    print('register_user handler is created and added to dispatcher!')

    # on noncommand
    dp.add_handler(MessageHandler(Filters.text, ask_text))
    print('ask_text handler is created and added to dispatcher!')

    # log all errors
    dp.add_error_handler(error)
    print('Error handler is added to dispatcher!')

    # Start the Bot
    updater.start_polling()
    print('Bot is started!')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()