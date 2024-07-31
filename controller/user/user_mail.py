import bcrypt
from apn_validators import validate
from flask import flash, redirect, request, url_for
from flask_mailman import EmailMessage

from config import USER_COLLECTION
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
    user, err = db.find_one(USER_COLLECTION, email)
    print("test")
    print(user)
    token = user["token"]
    reset_url = url_for("reset_password", token=token, _external=True)
    msg = EmailMessage(
        "Password Reset",
        f"Klik link berikut untuk mereset password: {reset_url}",
        "foodbridge@fastmail.com",
        [email["email"]],
    )
    msg.send()
    return redirect(url_for("user_sign_in"))


def reset_password(token):
    password, err = validate_password(request.form.to_dict())
    user, err = db.find_one(USER_COLLECTION, {"token": token})
    password_hash = bcrypt.hashpw(
        password["password"].encode("utf-8"), bcrypt.gensalt()
    )
    updated_password, err = db.update_one(
        USER_COLLECTION,
        {"token": token},
        {"token": db.randomStr(), "password": password_hash},
    )
    if err:
        flash(err, "error")

    flash("berhasil merubah password", "success")
    return redirect(url_for("user_sign_in"))
