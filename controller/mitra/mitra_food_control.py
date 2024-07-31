from datetime import datetime

import bcrypt
from apn_validators import validate
from flask import flash, jsonify, redirect, request, session, url_for

from config import FOOD_COLLECTION, MITRA_COLLECTION
from model import db
from schema.rules import Length, NotBlank, Password
from schema.UniqueRule import UniqueRule


def validate_create_stock(data):
    return validate(
        {
            "mitraId": [NotBlank()],
            "name": [NotBlank()],
            "price": [NotBlank()],
            "stock": [NotBlank()],
            "endAt": [NotBlank()],
        },
        data,
    )


def create():
    data, err = validate_create_stock(request.form.to_dict())
    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("mitra_stock"))
    food, err = db.insert_one(FOOD_COLLECTION, data)
    if err:
        flash(err, "error")
        return redirect(url_for("stock_create"))
    flash("berhasil membuat stock baru", "success")
    return redirect(url_for("mitra_stock"))
