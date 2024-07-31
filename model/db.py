from datetime import datetime, timedelta
from random import choice
from string import ascii_uppercase, digits
from typing import Any, Mapping, Optional, Sequence

from flask import flash, session
from pymongo import MongoClient, errors

from config import DATABASE_NAME, MITRA_COLLECTION, MONGO_URI, USER_COLLECTION

# utils


def randomStr(lenght: int = 12):
    return "".join(choice(ascii_uppercase + digits) for i in range(lenght))


def startOfDay(addDays=0):
    today = datetime.now()
    today += timedelta(days=addDays)
    return today.replace(hour=0, minute=0, second=0, microsecond=0)


def mitra_signed():
    mitraId = session.get("mitra_id")
    mitra, _ = find_one(MITRA_COLLECTION, {"_id": mitraId})
    return mitra


def user_signed():
    userId = session.get("user_id")
    user, _ = find_one(USER_COLLECTION, {"_id": userId})
    return user


# hashed = bcrypt.hashpw(data.get("password").encode("utf-8"), bcrypt.gensalt())

# TODO: tambahin contoh crud

__connection = None
__db = None


def list_to_flash(list_message, category):
    for message in list_message:
        flash(message, category)


def connection(force=False):
    global __connection

    if __connection is not None and not force:
        return __connection
    try:
        __connection = MongoClient(MONGO_URI)
        return __connection
    except errors.ConnectionFailure as con_fail:
        print(con_fail)
    except Exception as e:
        print(e)


def get_db():
    """get db connection"""
    global __db

    if __db is not None:
        return __db
    __db = connection()[DATABASE_NAME]
    return __db


# TODO: add func set_db if need to change db connection


def find_one(collection_name: str, filter=None, *args: Any, **kwargs: Any):
    data = None
    error = None

    try:
        collection = get_db()[collection_name]
        data = collection.find_one(filter, *args, **kwargs)
    except errors.PyMongoError as err:
        error = str(err)

    return data, error


def find(collection_name: str, *args: Any, **kwargs: Any):
    data = None
    error = None

    try:
        collection = get_db()[collection_name]
        data = collection.find(*args, **kwargs)
        data = list(data)
    except errors.PyMongoError as err:
        error = str(err)

    return data, error


def insert_one(
    collection_name: str,
    document,
    bypass_document_validation: bool = False,
    session=None,
    comment=None,
):
    data = None
    error = None

    try:
        document["createdAt"] = datetime.now()
        document["_id"] = randomStr()

        collection = get_db()[collection_name]
        data = collection.insert_one(
            document, bypass_document_validation, session, comment
        )
    except errors.PyMongoError as err:
        error = str(err)

    return data, error


def update_one(
    collection_name: str,
    filter: Mapping[str, Any],
    update,
    upsert: bool = False,
    bypass_document_validation: bool = False,
    collation=None,
    array_filters: Optional[Sequence[Mapping[str, Any]]] = None,
    hint=None,
    session=None,
    let: Optional[Mapping[str, Any]] = None,
    comment: Optional[Any] = None,
):
    data = None
    error = None

    try:
        collection = get_db()[collection_name]
        data = collection.update_one(
            filter,
            {"$set": update},
            upsert,
            bypass_document_validation,
            collation,
            array_filters,
            hint,
            session,
            let,
            comment,
        )
    except errors.PyMongoError as err:
        error = str(err)
        # error = "Something went wrong with the database. Please wait a moment and try again."

    return data, error


def update_one_default(
    collection_name: str,
    filter: Mapping[str, Any],
    update,
    upsert: bool = False,
    bypass_document_validation: bool = False,
    collation=None,
    array_filters: Optional[Sequence[Mapping[str, Any]]] = None,
    hint=None,
    session=None,
    let: Optional[Mapping[str, Any]] = None,
    comment: Optional[Any] = None,
):
    """tidak secara default menggunakan $set"""
    data = None
    error = None

    try:
        collection = get_db()[collection_name]
        data = collection.update_one(
            filter,
            update,
            upsert,
            bypass_document_validation,
            collation,
            array_filters,
            hint,
            session,
            let,
            comment,
        )
    except errors.PyMongoError as err:
        error = str(err)
        # error = "Something went wrong with the database. Please wait a moment and try again."

    return data, error


def delete_one(
    collection_name: str,
    filter: Mapping[str, Any],
    collation=None,
    hint=None,
    session=None,
    let=None,
    comment=None,
):
    data = None
    error = None

    try:
        collection = get_db()[collection_name]
        data = collection.delete_one(filter, collation, hint, session, let, comment)
    except errors.PyMongoError as err:
        error = str(err)

    return data, error
