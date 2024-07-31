from datetime import datetime, timedelta

import bcrypt
from flask import flash, redirect, request, session, url_for

from config import MITRA_COLLECTION, USER_COLLECTION
from controller.user.auth import validate_user_sign_in
from model import db
from schema.UniqueRule import ExistsRule


def admin_sign_in():
    data, err = validate_user_sign_in(request.form.to_dict())
    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("admin_sign_in"))

    user, err = db.find_one(USER_COLLECTION, {"email": data["email"]})
    if err:
        flash(err, "error")
        return redirect(url_for("admin_sign_in"))

    if user is None:
        flash("email atau password tidak valid", "error")
        return redirect(url_for("admin_sign_in"))

    if not bcrypt.checkpw(data["password"].encode("utf-8"), user.get("password")):
        flash("email atau password tidak valid", "error")
        return redirect(url_for("admin_sign_in"))

    session["user_id"] = user["_id"]
    return redirect(url_for("admin_confirm_user"))


def get_confirm_user():
    users, err = db.find(USER_COLLECTION, {"status": {"$in": ["PENDING", "REJECT"]}})

    return users


def admin_confirm_user():
    err = ExistsRule(USER_COLLECTION, "_id").validate(
        request.form.get("_id"), "id user"
    )
    if err:
        flash(err, "error")
        return redirect(url_for("admin_confirm_user"))
    user, err = db.find_one(USER_COLLECTION, {"_id": request.form.get("_id")})
    new_status = request.form.get("status")
    if new_status == "APPROVE":
        expiredAt = datetime.now() + timedelta(days=90)
    else:
        expiredAt = None
    updated_user, error = db.update_one(
        USER_COLLECTION,
        {"_id": user.get("_id")},
        {"status": new_status, "expiredAt": expiredAt},
    )
    if error:
        flash(error, "error")
    flash("berhasil merubah status user", "success")
    return redirect(url_for("admin_confirm_user"))


def get_confirm_admin():
    users, err = db.find(MITRA_COLLECTION, {"status": {"$in": ["PENDING", "REJECT"]}})
    return users


def admin_confirm_mitra():
    err = ExistsRule(MITRA_COLLECTION, "_id").validate(
        request.form.get("_id"), "id mitra"
    )
    if err:
        flash(err, "error")
        return redirect(url_for("admin_confirm_mitra"))

    mitra, err = db.find_one(MITRA_COLLECTION, {"_id": request.form.get("_id")})
    new_status = request.form.get("status")
    if new_status == "APPROVE":
        verifyAt = datetime.now() + timedelta(days=90)
    else:
        verifyAt = None
    updated_user, error = db.update_one(
        MITRA_COLLECTION,
        {"_id": mitra.get("_id")},
        {"status": new_status, "verifyAt": verifyAt},
    )
    if error:
        flash(error, "error")
    flash("berhasil merubah status mitra", "success")
    return redirect(url_for("admin_confirm_mitra"))
