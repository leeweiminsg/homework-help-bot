from datetime import datetime
import logging

from pymongo import MongoClient

# Enable logging to handle uncaught exceptions
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MongoDB instance: default host and port are localhost and 27017
client = MongoClient(
    'mongodb+srv://admin:14&Chs8FecVro!sVrD12iP0$k@homework-help-cluster-dlv15.mongodb.net/test?retryWrites=true')
print('MongoDB instance is created!')

# Create database
db = client.homework_help
print('homework_help database is created!')
# Create user, tutor and question collection
users_collection = db.users_collection
tutor_collection = db.tutor_collection
question_collection = db.question_collection
print('user, tutor and question collections are created!')


def create_user_document(user_id, username):
    """Creates user document in user collection"""
    user_document = {
        "user_id": user_id,
        "username": username,
        "is_tutor": False,
        "questions": [],
        "created_at": datetime.utcnow()
    }
    users_collection.insert_one(user_document)
    logger.info(f"Inserted user into user collection: {user_document}")


def get_user_document(user_id):
    """Tries to get user document from user collection; if it fails returns None"""
    return users_collection.find_one({"user_id": user_id})


def create_question_document(question, user_id, username):
    """Creates question document in question collection"""
    question_document = {
        "question": question,
        "answer": None,
        "user_id": user_id,
        "username": username,
        "tutor_id": None,
        "tutorname": None,
        "is_answered": False,
        "is_deleted": False,
        "answered_at": None,
        "created_at": datetime.utcnow(),
        "deleted_at": None
    }
    question_collection.insert_one(question_document)
    logger.info(
        f"Inserted question into question collection: {question_document}")


def get_question(user_id):
    return question_collection.find_one({"user_id": user_id})


def get_unanswered_question():
    return question_collection.find_one({"is_answered": False})


def get_answered_question():
    return question_collection.find_one({"is_answered": True, "is_deleted": False})


def update_question_document(question_id, answer, tutor_id, tutorname):
    question_collection.update_one({"_id": question_id}, {
                                   "$set": {"answer": answer, "tutor_id": tutor_id, "tutorname": tutorname, "is_answered": True, "answered_at": datetime.utcnow()}})
    print(f"Updated answer in question collection with tutor_id: {tutor_id}")


def delete_question_document(question_id):
    question_collection.update_one({"_id": question_id}, {
                                   "$set": {"is_deleted": True, "deleted_at": datetime.utcnow()}})
