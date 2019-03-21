#Refer to echobot2: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
from datetime import datetime
import logging

from pymongo import MongoClient

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging to handle uncaught exceptions
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

token = '837770119:AAEmP97SuF0moJezC0jipSHz5Uy-CXqNNoI'

# Create MongoDB instance: default host and port are localhost and 27017
client = MongoClient()
print('MongoDB instance is created!')

# Create database
db = client.homework_help
print('homework_help database is created!')
# Create user, tutor and question collection
users_collection = db.users_collection
tutor_collection = db.tutor_collection
question_collection = db.question_collection
print('user, tutor and question collections are created!')

def start(update, context):
    """on /start command: Welcomes user, gets user details"""
    update.message.reply_text("Welcome to sgHomeworkHelp!")
    user = update.message.from_user
    get_user_details(user)
    update.message.reply_text(f"Hi, {user.full_name}!")

def get_user_details(user):
    """Gets user details from User object"""
    user_id = user.id
    username = user.full_name
    print(f"Got user details: {user_id} {username}")

    user_document = get_user_document(user_id)

    if not user_document:
        create_user_document(user_id, username)
    else:
        update_user_document(user_id, "start")

def create_user_document(user_id, username):
    """Creates user document in user collection"""
    user_document = {
        "user_id": user_id,
        "username": username,
        "user_state": "START",
        "created_at": datetime.utcnow()
    }
    users_collection.insert_one(user_document)
    print(f"Inserted user into user collection: {user_document}")

def get_user_document(user_id):
    """Tries to get user document from user collection; if it fails returns None"""
    return users_collection.find_one({"user_id": user_id})

def update_user_document(user_id, user_state):
    """Updates user_state in user document"""

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('/help was entered as a command!\nWhat do you need help with?')

def ask(update, context):
    """Send a message when the command /ask is issued."""
    update.message.reply_text("/ask was entered as a command!\nWhat's your question?")

#NOTE: both username and tutorname are the same (for testing)
def ask_text(update, context, args):
    """after /ask command: Sends a message when user asks a question (text format)."""
    user = update.message.from_user
    user_id = user.id
    username = user.full_name
    question = update.message.text
    update.message.reply_text(f"Hi {username}, your question is: {question}\nIt is awaiting reply!")
    create_question_document(question, user_id, username)

def create_question_document(question, user_id, username):
    """Creates question document in question collection"""
    question_document = {
        "question": question,
        "user_id": user_id,
        "username": username,
        "tutor_id": user_id,
        "tutorname": username,
        "is_answered": "false",
        "created_at": datetime.utcnow()
    }
    question_collection.insert_one(question_document)
    print(f"Inserted question into question collection: {question_document}")

def answer(update, context):
    """Send a message when the command /answer is issued."""
    update.message.reply_text("/answer was entered as a command!\nHere's a question for you:")

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
