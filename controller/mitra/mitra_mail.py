import bcrypt
from apn_validators import validate
from flask import flash, redirect, request, url_for
from flask_mailman import EmailMessage, Mail

from config import MITRA_COLLECTION
from model import db
from schema.rules import Email, NotBlank, Password


def validate_email(data):
    return validate(
        {
            "email": [NotBlank(), Email()],
        },
        data,
        is_err_to_list=True,
    )


def validate_password(data):
    return validate(
        {
            "password": [NotBlank(), Password()],
        },
        data,
        is_err_to_list=True,
    )


def send_mail():
    email, err = validate_email(request.form.to_dict())
    mitra, err = db.find_one(MITRA_COLLECTION, email)
    print(mitra)
    token = mitra["token"]
    reset_url = url_for("mitra_reset_password", token=token, _external=True)
    msg = EmailMessage(
        "Password Reset",
        f"Klik link berikut untuk mereset password: {reset_url}",
        "foodbridge@fastmail.com",
        [email["email"]],
    )
    msg.send()
    return redirect(url_for("mitra_sign_in"))


def reset_password(token):
    password, err = validate_password(request.form.to_dict())
    mitra, err = db.find_one(MITRA_COLLECTION, {"token": token})
    password_hash = bcrypt.hashpw(
        password["password"].encode("utf-8"), bcrypt.gensalt()
    )
    updated_password, err = db.update_one(
        MITRA_COLLECTION,
        {"token": token},
        {"token": db.randomStr(), "password": password_hash},
    )
    if err:
        flash(err, "error")

    flash("berhasil merubah password", "success")
    return redirect(url_for("mitra_sign_in"))
