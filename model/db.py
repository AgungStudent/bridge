from pymongo import MongoClient

from config import DATABASE_NAME, MONGO_URI


def find(collection_name, *args, **kwargs):
    connection = MongoClient(MONGO_URI)
    db = connection[DATABASE_NAME]
    result = db[collection_name].find(args, kwargs)
    return result


def find_one(collection_name, filter, *args, **kwargs):
    connection = MongoClient(MONGO_URI)
    db = connection[DATABASE_NAME]
    result = db[collection_name].find_one(args, kwargs)
    return result
