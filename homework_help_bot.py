# Refer to echobot2: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
from datetime import datetime
import logging

from pymongo import MongoClient

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# Conversation states
SELECT, ASK, ANSWER, GET_ANSWER = range(4)

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

    start_message = f"Hi, {user.full_name}!\nPlease select an action:"
    start_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Ask a question", callback_data="ASK")],
         [InlineKeyboardButton("Answer question", callback_data="ANSWER")],
         [InlineKeyboardButton("Get answer", callback_data="GET_ANSWER")]]
    )

    update.message.reply_text(
        start_message,  reply_markup=start_keyboard)

    return SELECT


def select(update, context):
    query = update.callback_query
    choice = query.data
    user_id = query.from_user.id

    print(f"User has selected {choice}")

    if choice == "ASK":
        query.edit_message_text(f"Please enter your question:")
        return ASK
    elif choice == "ANSWER":
        question = get_question_document(user_id)["question"]
        query.edit_message_text(
            f"Here is a question for you:\n\n{question}\n\nPlease answer it:")
        return ANSWER
    elif choice == "GET_ANSWER":
        query.edit_message_text(
            f"You have asked the question: {get_question(user_id)} Here is your answer:\n{get_answer(user_id)}\
            Type /start to return to main menu")
        return ConversationHandler.END


def get_user_details(user):
    """Gets user details from User object"""
    user_id = user.id
    username = user.full_name
    print(f"Got user details: {user_id} {username}")

    user_document = get_user_document(user_id)

    if not user_document:
        create_user_document(user_id, username)


def create_user_document(user_id, username):
    """Creates user document in user collection"""
    user_document = {
        "user_id": user_id,
        "username": username,
        "created_at": datetime.utcnow()
    }
    users_collection.insert_one(user_document)
    print(f"Inserted user into user collection: {user_document}")


def get_user_document(user_id):
    """Tries to get user document from user collection; if it fails returns None"""
    return users_collection.find_one({"user_id": user_id})


# TODO: Update help command
def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        '/help was entered as a command!\nWhat do you need help with?')

# NOTE: both username and tutorname are the same (for testing)


def ask(update, context):
    """Sends a message when user asks a question (text format)."""
    user = update.message.from_user
    user_id = user.id
    username = user.full_name
    question = update.message.text

    create_question_document(question, user_id, username)

    update.message.reply_text(
        f"Hi {username}, your question is: {question}\nIt is awaiting reply! Type /start to return to main menu")

    return ConversationHandler.END


def answer(update, context):
    """Collects the answer (text format)"""
    user = update.message.from_user
    user_id = user.id
    username = user.full_name
    answer = update.message.text

    update_question_document(answer, user_id)

    update.message.reply_text(
        f"Hi {username}, your answer is: {answer}\nIt has been sent! Type /start to return to main menu")

    return ConversationHandler.END


def get_question(user_id):
    return get_question_document(user_id)["question"]


def get_answer(user_id):
    return get_question_document(user_id)["answer"]


def create_question_document(question, user_id, username):
    """Creates question document in question collection"""
    question_document = {
        "question": question,
        "answer": "",
        "user_id": user_id,
        "username": username,
        "tutor_id": user_id,
        "tutorname": username,
        "is_answered": "false",
        "created_at": datetime.utcnow()
    }
    question_collection.insert_one(question_document)
    print(f"Inserted question into question collection: {question_document}")


# TODO: seperate tutor_id and user_id
def get_question_document(tutor_id):
    """Creates question document in question collection"""
    return question_collection.find_one({"tutor_id": tutor_id})


def update_question_document(answer, tutor_id):
    """Updates answer in question document in question collection"""
    question_collection.update_one({"tutor_id": tutor_id}, {
                                   "$set": {"answer": answer, }})
    print(f"Updated answer in question collection with tutor_id: {tutor_id}")


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

    # Use conversation handler to handle states
    conversation_handler = ConversationHandler(
        [CommandHandler('start', start)],
        {
            SELECT: [CallbackQueryHandler(select)],
            ASK: [MessageHandler(Filters.text, ask)],
            ANSWER: [MessageHandler(Filters.text, answer)],
            GET_ANSWER: [CommandHandler('get_answer', get_answer)]
        },
        [CommandHandler('help', help)],
    )

    dp.add_handler(conversation_handler)

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
