import os
import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import database
from database import get_user_document, create_user_document, get_question, get_unanswered_question, get_answered_question, create_question_document, update_question_document, delete_question_document

import config

# Conversation states
ASK_INPUT, ANSWER_INPUT, ASK_PHOTO, ANSWER_PHOTO = range(4)

# Enable logging to handle uncaught exceptions
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

start_keyboard_markup = ReplyKeyboardMarkup([["/menu"]],
                                            one_time_keyboard=True,
                                            resize_keyboard=True)


def start(update, context):
    """on /start command: Welcomes user, retrieve and store user details and displays start menu. All users are treated as normal users (is_tutor = false)"""
    user = update.message.from_user
    context.user_data["user_id"], context.user_data["full_name"] = user.id, user.full_name

    get_user_details(user)

    update.message.reply_text(
        f"Hi {context.user_data['full_name']}, I'm sgHomeworkHelp_Bot!\n\nSelect /menu to display a menu of options", reply_markup=start_keyboard_markup)


def menu(update, context):
    """on /menu command: Check user role, and display menu of options accordingly"""

    if is_tutor(context.user_data["user_id"]):
        menu_keyboard = [["/answer"]]
    else:
        menu_keyboard = [["/ask"]]

    menu_keyboard_markup = ReplyKeyboardMarkup(menu_keyboard,
                                               one_time_keyboard=True,
                                               resize_keyboard=True)

    update.message.reply_text(
        "Please select an action:",  reply_markup=menu_keyboard_markup)


def get_user_details(user):
    """Gets user details from User object"""
    user_id = user.id
    username = user.full_name
    logger.info(f"Got user details: {user_id} {username}")

    if not get_user_document(user_id):
        create_user_document(user_id, username)


def is_tutor(user_id):
    """Checks is_tutor flag in User object"""
    user_document = get_user_document(user_id)

    return user_document["is_tutor"]


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        '/help was entered as a command!\nWhat do you need help with?')


def ask(update, context):
    update.message.reply_text(f"Please enter your question:")

    return ASK_INPUT


def ask_text(update, context):
    question = update.message.text

    question_id = create_question_document(
        question, context.user_data["user_id"], context.user_data["full_name"]).inserted_id

    context.chat_data["unanswered_question"] = database.get_question(
        question_id)

    skip_keyboard = [["Skip"]]
    skip_keyboard_markup = ReplyKeyboardMarkup(skip_keyboard,
                                               one_time_keyboard=True,
                                               resize_keyboard=True)
    update.message.reply_text(
        f"Please upload the associated image of the question (or enter 'Skip' if you don\'t want to.):",  reply_markup=skip_keyboard_markup)

    return ASK_PHOTO


def ask_photo(update, context):
    if not update.message.text:
        photo_file = update.message.photo[-1].get_file()
        photo_file_url = photo_file.download(
            f"{context.user_data['full_name']}_homework_photo.jpg")
        database.set_question_photo(
            context.chat_data["unanswered_question"]["_id"], photo_file_url)

        context.bot.send_photo(
            config.TUTOR_ID, open(f"{context.user_data['full_name']}_homework_photo.jpg", "rb"))
        os.remove(f"{context.user_data['full_name']}_homework_photo.jpg")

    update.message.reply_text(
        f"Your question was sent!\n\nSelect /menu to display a menu of options", reply_markup=start_keyboard_markup)

    message = f"Here is a question for you by {context.chat_data['unanswered_question']['username']}:\n\n{context.chat_data['unanswered_question']['question']}\n\nPlease answer it: "
    context.bot.send_message(config.TUTOR_ID, message,
                             reply_markup=start_keyboard_markup)

    del context.chat_data["unanswered_question"]

    return ConversationHandler.END


def answer(update, context):
    context.chat_data["question_document"] = question_document = get_unanswered_question()

    if not question_document:
        update.message.reply_text(
            f"There are no questions available!", reply_markup=start_keyboard_markup)

        return ConversationHandler.END
    else:
        if question_document["question_photo"]:
            with open(f"{question_document['username']}_question_photo.jpg", "wb") as file:
                file.write(question_document['question_photo'])
            update.message.reply_photo(
                open(f"{question_document['username']}_question_photo.jpg", "rb"))
            os.remove(f"{question_document['username']}_question_photo.jpg")

        update.message.reply_text(
            f"Here is a question for you by {question_document['username']}:\n\n{question_document['question']}\n\nPlease answer it:")

    return ANSWER_INPUT


def answer_text(update, context):
    answer = update.message.text
    question_id = context.chat_data["question_document"]["_id"]

    context.chat_data["answered_question"] = update_question_document(
        question_id, answer, context.user_data["user_id"], context.user_data["full_name"])

    skip_keyboard = [["Skip"]]
    skip_keyboard_markup = ReplyKeyboardMarkup(skip_keyboard,
                                               one_time_keyboard=True,
                                               resize_keyboard=True)
    update.message.reply_text(
        f"Please upload the associated image of the question (or enter 'Skip' if you don\'t want to.):",  reply_markup=skip_keyboard_markup)

    return ANSWER_PHOTO


def answer_photo(update, context):
    answered_question = context.chat_data["answered_question"]

    if not update.message.text:
        photo_file = update.message.photo[-1].get_file()
        photo_file_url = photo_file.download(
            f"{context.user_data['full_name']}_answer_photo.jpg")
        database.set_answer_photo(
            answered_question["_id"], photo_file_url)

        context.bot.send_photo(answered_question["user_id"], open(
            f"{context.user_data['full_name']}_answer_photo.jpg", "rb"))
        os.remove(f"{context.user_data['full_name']}_answer_photo.jpg")

    update.message.reply_text(
        f"Your answer was sent!\n\nSelect /menu to display a menu of options", reply_markup=start_keyboard_markup)

    message = (f'You have asked the question: \n\n{answered_question["question"]}\n\n'
               f'Here is your answer: \n\n{answered_question["answer"]}\n\n'
               f'It was answered by: {answered_question["tutorname"]}\n\nSelect /menu to display a menu of options')

    context.bot.send_message(
        answered_question["user_id"], message, reply_markup=start_keyboard_markup)

    delete_question_document(answered_question["_id"])

    del context.chat_data["question_document"], context.chat_data["answered_question"]

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    updater = Updater(token=config.TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Use conversation handler to handle states
    ask_conversation = ConversationHandler(
        [CommandHandler('ask', ask, pass_user_data=True, pass_chat_data=True)],
        {ASK_INPUT: [MessageHandler(Filters.text, ask_text, pass_user_data=True, pass_chat_data=True)],
         ASK_PHOTO: [MessageHandler(Filters.photo | Filters.text, ask_photo, pass_user_data=True, pass_chat_data=True)],
         },
        [CommandHandler('help', help)],
    )

    answer_conversation = ConversationHandler(
        [CommandHandler('answer', answer, pass_user_data=True,
                        pass_chat_data=True)],
        {ANSWER_INPUT: [MessageHandler(Filters.text, answer_text, pass_user_data=True, pass_chat_data=True)],
         ANSWER_PHOTO: [MessageHandler(Filters.photo | Filters.text, answer_photo, pass_user_data=True, pass_chat_data=True)],
         },
        [CommandHandler('help', help)],
    )

    dp.add_handler(ask_conversation)
    dp.add_handler(answer_conversation)

    dp.add_handler(CommandHandler(
        'start', start, pass_user_data=True, pass_chat_data=True))
    dp.add_handler(CommandHandler(
        'menu', menu, pass_user_data=True, pass_chat_data=True))

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
