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

#TODO: refactor proccessing of user details
def start(update, context):
    """on /start command: Welcomes user, gets user details"""
    update.message.reply_text("Welcome to sgHomeworkHelp!")
    get_user_details(update.message.from_user)
    update.message.reply_text(f"Hi, {username}!")

def get_user_details(user):
    """Extracts user details from User object"""
    global user_id, username
    user_id = user.id
    username = user.full_name
    print(f"Processed user: {user_id} {username}")

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('/help was entered as a command!\nWhat do you need help with?')

def ask(update, context):
    """Send a message when the command /ask is issued."""
    update.message.reply_text("/ask was entered as a command!\nWhat's your question?")

#TODO: refactor username
def ask_text(update, context):
    """Send a message when user asks a question (text format). NOTE: both username and tutorname are the same (for testing)"""
    question = update.message.text
    username = f"{update.message.from_user.first_name} {update.message.from_user.last_name}"
    update.message.reply_text(f"Hi {username}, your question is: {question}\nIt is awaiting reply!")
    question_document = get_question_document(question, username)
    print(f"Insert question document: {question_document}")
    question_insert_result = question_collection.insert_one(question_document)
    print(f"Is insert question operation acknowledged? : {question_insert_result.acknowledged}")

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

def get_question_document(question, username):
    """Convert question to document. NOTE: datetime is in utc format, username and tutorname are the same"""
    question_document = {
        "question": question,
        "username": username,
        "tutorname": username,
        "created_at": datetime.utcnow()
    }
    return question_document

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
