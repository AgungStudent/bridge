from datetime import datetime

from flask import flash, redirect, render_template, request, session, url_for

from config import FOOD_COLLECTION, MITRA_COLLECTION
from model import db


def history():
    mitra_id = session.get("mitra_id")
    foods, err = db.find(FOOD_COLLECTION, {"mitra_id": mitra_id})
    if err:
        flash(err, "error")

    list_histories = []
    for food in foods:
        for claim in food.get("claims"):
            list_histories.append(
                {
                    "name_food": food.get("name"),
                    "user_name": claim.get("userName"),
                    "quantity": claim.get("quantity"),
                    "point": claim.get("point"),
                    "claimAt": claim.get("claimAt"),
                }
            )
    return list_histories
