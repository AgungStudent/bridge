import bcrypt
from apn_validators import validate
from flask import flash, redirect, request, session, url_for
from werkzeug.utils import secure_filename

from config import MITRA_COLLECTION
from model import db
from schema.rules import AllowedFile, Email, Equals, Length, NotBlank, Password
from schema.UniqueRule import UniqueRule


def validate_new_mitra(data, is_sign_up=True):
    schema = {
        "email": [NotBlank(), Email(), UniqueRule(MITRA_COLLECTION, "email")],
        "password": [NotBlank(), Password()],
        "name": [NotBlank(), Length(4, 50)],
        "city": [NotBlank()],
        "address": [NotBlank()],
        "lat": [NotBlank()],
        "lon": [NotBlank()],
        "ktp": [NotBlank(), AllowedFile()],
        "npwp": [NotBlank(), AllowedFile()],
    }
    if is_sign_up:
        schema["terms"] = [NotBlank(), Equals("1")]

    return validate(
        schema,
        data,
        is_err_to_list=True,
    )


def mitra_sign_up():
    if "ktp" not in request.files:
        flash("upload ktp dulu")
        return redirect(url_for("mitra_sign_up"))
    if "npwp" not in request.files:
        flash("upload npwp dulu")
        return redirect(url_for("mitra_sign_up"))

    data = request.form.to_dict()
    fileKtp = request.files.get("ktp")
    fileNpwp = request.files.get("npwp")
    data, err = validate_new_mitra(data)
    ktpFilename = fileKtp.filename if fileKtp.filename else ""
    npwpFilename = fileNpwp.filename if fileNpwp.filename else ""
    data["ktp"] = db.randomStr() + secure_filename(ktpFilename)
    data["npwp"] = db.randomStr() + secure_filename(npwpFilename)

    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("mitra_sign_up"))

    data["verifyAt"] = None
    data["parentId"] = None
    data["password"] = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
    user, err = db.insert_one(MITRA_COLLECTION, data)
    if err:
        flash(err)
        return redirect(url_for("mitra_sign_up"))
    fileKtp.save("static/mitra/ktp/" + ktpFilename)
    fileNpwp.save("static/mitra/npwp/" + npwpFilename)

    flash("berhasil registrasi, silahkan login", "success")
    return redirect(url_for("mitra_sign_in"))


def mitra_sign_in():
    data = request.form
    email = data.get("email")
    password = data.get("password")
    user, err = db.find_one(MITRA_COLLECTION, {"email": email})

    if err:
        flash(err, "error")
        return redirect(url_for("user_sign_in"))
    if user is None:
        flash("username atau password salah")
        return redirect(url_for("mitra_sign_in"))
    if bcrypt.checkpw(password.encode("utf-8"), user.get("password")):
        session["mitra_id"] = str(user.get("_id"))
        session["is_mitra_parent"] = bool(user.get("parentId"))
        return redirect(url_for("mitra_stock"))

    flash("email atau password salah")
    return redirect(url_for("mitra_sign_in"))
