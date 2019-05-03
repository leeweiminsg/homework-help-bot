import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from database import get_user_document, create_user_document, get_question, get_unanswered_question, get_answered_question, create_question_document, update_question_document, delete_question_document

# Conversation states
SELECT, ASK, ANSWER = range(3)

# Enable logging to handle uncaught exceptions
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

token = '837770119:AAEmP97SuF0moJezC0jipSHz5Uy-CXqNNoI'

start_keyboard_markup = ReplyKeyboardMarkup([['/menu']],
                                            one_time_keyboard=True,
                                            resize_keyboard=True)


def start(update, context):
    """on /start command: Welcomes user, gets user details and displays start menu. All users are treated as normal users (is_tutor = false)"""
    user = update.message.from_user
    get_user_details(user)

    update.message.reply_text(
        f"Hi {user.full_name}, I'm sgHomeworkHelp_Bot!\n\nSelect /menu to display a menu of options", reply_markup=start_keyboard_markup)


def menu(update, context):
    """on /menu command: Check user role, and display menu of options accordingly"""
    # menu_keyboard = InlineKeyboardMarkup(
    #     [[InlineKeyboardButton("Ask a question", callback_data="ASK")],
    #      [InlineKeyboardButton("Answer question", callback_data="ANSWER")],
    #      [InlineKeyboardButton("Get answer", callback_data="GET_ANSWER")]]
    # )
    user = update.message.from_user

    if is_tutor(user):
        menu_keyboard = [["Answer question"]]
    else:
        menu_keyboard = [["Ask question"], ["Get answer"]]

    menu_keyboard_markup = ReplyKeyboardMarkup(menu_keyboard,
                                               one_time_keyboard=True,
                                               resize_keyboard=True)

    update.message.reply_text(
        "Please select an action:",  reply_markup=menu_keyboard_markup)

    return SELECT


def select(update, context):
    # query = update.callback_query
    choice = update.message.text
    user_id = update.message.from_user.id
    # user_id = query.from_user.id

    if choice == "Ask question":
        update.message.reply_text(f"Please enter your question:")
        return ASK
    elif choice == "Answer question":
        context.chat_data["question_document"] = question_document = get_unanswered_question(
        )
        if question_document is None:
            update.message.reply_text(
                f"There are no questions available!", reply_markup=start_keyboard_markup)
            return ConversationHandler.END
        else:
            question = question_document["question"]
            update.message.reply_text(
                f"Here is a question for you:\n\n{question}\n\nPlease answer it:")
            return ANSWER
    elif choice == "Get answer":
        answered_question = get_answered_question()
        if answered_question is None:
            message = f"There are no answered questions!"
        else:
            message = (f'You have asked the question: \n\n{answered_question["question"]}\n\n'
                       f'Here is your answer: \n\n{answered_question["answer"]}\n\n'
                       f'It was answered by: {answered_question["tutorname"]}\n\nSelect /menu to display a menu of options')
            delete_question_document(answered_question["_id"])
        update.message.reply_text(message, reply_markup=start_keyboard_markup)
        return ConversationHandler.END


def get_user_details(user):
    """Gets user details from User object"""
    user_id = user.id
    username = user.full_name
    logger.info(f"Got user details: {user_id} {username}")

    if not get_user_document(user_id):
        create_user_document(user_id, username)


def is_tutor(user):
    """Checks is_tutor flag in User object"""
    user_id = user.id
    user_document = get_user_document(user_id)

    return user_document["is_tutor"]


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
        f"You have asked the question: {question}\n\nIt has been sent!\n\nSelect /menu to display a menu of options", reply_markup=start_keyboard_markup)

    return ConversationHandler.END


def answer(update, context):
    """Collects the answer (text format)"""
    user = update.message.from_user
    user_id = user.id
    username = user.full_name
    question_id = context.chat_data["question_document"]["_id"]
    answer = update.message.text

    update_question_document(question_id, answer, user_id, username)

    update.message.reply_text(
        f"Your have answered: {answer}\n\nIt has been sent!\n\nSelect /menu to display a menu of options", reply_markup=start_keyboard_markup)

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    updater = Updater(token=token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Use conversation handler to handle states
    conversation_handler = ConversationHandler(
        [CommandHandler('menu', menu)],
        {
            SELECT: [MessageHandler(Filters.text, select, pass_chat_data=True)],
            ASK: [MessageHandler(Filters.text, ask)],
            ANSWER: [MessageHandler(Filters.text, answer, pass_chat_data=True)]
        },
        [CommandHandler('help', help)],
    )

    dp.add_handler(conversation_handler)

    dp.add_handler(CommandHandler('start', start))

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
