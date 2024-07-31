from datetime import datetime

import bcrypt
from apn_validators import validate
from flask import flash, redirect, request, session, url_for
from werkzeug.utils import secure_filename

from config import USER_COLLECTION
from model import db
from schema.rules import AllowedFile, Email, Length, NotBlank, Password
from schema.UniqueRule import UniqueRule


def validate_user_sign_up(data):
    return validate(
        {
            "name": [NotBlank(), Length(3, 50)],
            "sktm": [NotBlank(), AllowedFile()],
            "password": [NotBlank(), Password()],
            "ktp": [NotBlank(), AllowedFile()],
            "email": [NotBlank(), Email(), UniqueRule(USER_COLLECTION, "email")],
            "city": [NotBlank()],
            "address": [NotBlank()],
            "lat": [NotBlank()],
            "lon": [NotBlank()],
        },
        data,
        is_err_to_list=True,
    )


def validate_user_sign_in(data):
    return validate(
        {
            "email": [NotBlank()],
            "password": [NotBlank(), Password()],
        },
        data,
        is_err_to_list=True,
    )


def user_sign_in():
    # check input harus diisi
    data, err = validate_user_sign_in(request.form.to_dict())
    # kalau ada error pas input
    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("user_sign_in"))

    # coba ambil data user
    user, err = db.find_one(USER_COLLECTION, {"email": data["email"]})
    # kalau ada error ketika query
    if err:
        flash(err, "error")
        return redirect(url_for("user_sign_in"))
    # kalau tidak ketemu data user
    if user is None:
        flash("username atau password salah")
        return redirect(url_for("user_sign_in"))
    # kalau password tidak pas
    if not bcrypt.checkpw(data["password"].encode("utf-8"), user["password"]):
        flash("username atau password salah")
        return redirect(url_for("user_sign_in"))
    # kalau belum di verifikasi admin atau kalau sudah lewat expiredAt
    if user["expiredAt"] is None:
        if user["status"] == "PENDING":
            session["user_id"] = user["_id"]
            session["status"] = user["status"]
            return redirect(url_for("user_verif"))
        elif user["status"] == "REJECT":
            session["user_id"] = user["_id"]
            session["status"] = user["status"]
            return redirect(url_for("user_verif"))
        elif user["status"] == "APPROVE":
            session["user_id"] = user["_id"]
            session["status"] = user["status"]
            return redirect(url_for("user_histories"))
    if user.get("expiredAt") < datetime.now():
        session["user_id"] = user["_id"]
        session["status"] = user["status"]
        status, err = db.update_one(
            USER_COLLECTION, {"_id": session.get("user_id")}, {"status": "EXPIRED"}
        )
        if err:
            flash(err)
            return redirect(url_for("user_verif"))
        return redirect(url_for("user_verif"))
    session["user_id"] = user["_id"]
    return redirect(url_for("user_histories"))


def user_sign_up():
    if "sktm" not in request.files:
        flash("upload sktm dulu")
        return redirect(url_for("user_sign_up"))
    data = request.form.to_dict()
    file_sktm = request.files["sktm"]
    filename = file_sktm.filename if file_sktm.filename else ""
    data["sktm"] = db.randomStr() + secure_filename(filename)

    if "ktp" not in request.files:
        flash("upload ktp dulu")
        return redirect(url_for("user_sign_up"))
    file_ktp = request.files["ktp"]
    filename = file_ktp.filename if file_ktp.filename else ""
    data["ktp"] = db.randomStr() + secure_filename(filename)

    data, err = validate_user_sign_up(data)
    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("user_sign_up"))
    data["role"] = "user"
    file_sktm.save("static/sktm/" + data["sktm"])
    file_ktp.save("static/ktp/" + data["ktp"])

    data["password"] = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
    data["expiredAt"] = None  # when SKTM verified then change to date
    data["balance"] = 100
    data["status"] = "PENDING"
    data["token"] = db.randomStr(6)
    data["bookmark_mitra"] = []

    user, err = db.insert_one(USER_COLLECTION, data)
    if err:
        flash(err)
        return redirect(url_for("user_sign_up"))
    return redirect(url_for("user_sign_in"))


def user_profile():
    if "user_id" in session and session.get("user_id") is not None:
        data, _ = db.find_one(USER_COLLECTION, {"_id": session.get("user_id")})
        return data
    return None
