from config import USER_COLLECTION
from model import db


def schadule_generate_token():
    users, err = db.find(USER_COLLECTION, {})
    for user in users:
        user["balance"] = 60
        db.update_one(USER_COLLECTION, {"_id": user.get("_id")}, user)
