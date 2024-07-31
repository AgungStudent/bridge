import bcrypt
from apn_validators import validate
from flask import flash, redirect, request, session, url_for

from config import MITRA_COLLECTION
from model import db
from schema.rules import Email, Length, NotBlank, Password
from schema.UniqueRule import UniqueRule


def validate_sign_in(data):
    return validate(
        {
            "email": [NotBlank(), Email(), Length(5, 50),UniqueRule(MITRA_COLLECTION,'email')],
            "password": [NotBlank(), Password()],
        },
        data,
    )


def validate_sign_up(data):
    return validate({"email": [NotBlank()], "password": [NotBlank()]}, data)


def sign_in():
    data, err = validate_sign_in(request.form.to_dict())
    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("mitra_sign_in"))

    mitra, err = db.find_one(MITRA_COLLECTION, {"email", data.get("email")})
    if err:
        flash(err, "error")
        return redirect(url_for("mitra_sign_in"))
    if mitra is None:
        flash("email atau password tidak ditemukkan", "error")
        return redirect(url_for("mitra_sign_in"))
    if bcrypt.checkpw(mitra.get("password"), data.get("password")):
        flash("email atau password tidak ditemukkan", "error")
        return redirect(url_for("mitra_sign_in"))

    session["mitra_id"] = mitra.get("_id")
    return redirect(url_for("mitra_index"))


def sign_up():
    data, err = validate_sign_up(request.form.to_dict())
    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("mitra_sign_in"))
