from flask import flash, redirect, request, session, url_for

from config import FOOD_COLLECTION, MITRA_COLLECTION, USER_COLLECTION
from model import db
from model.db import user_signed
from schema.UniqueRule import ExistsRule


def add_bookmark():
    mitra_id = request.args.get("mitra_id")
    err = ExistsRule(MITRA_COLLECTION, "_id").validate(mitra_id, "id")
    if err:
        flash(err, "error")
        return redirect(url_for("user_mitra"))
    user = user_signed()
    if user is None:
        flash("user not found", "error")
        return redirect(url_for("user_mitra"))

    user_bookmark = user.get("bookmark_mitra", [])
    if mitra_id in user_bookmark:
        user_bookmark.remove(mitra_id)
    else:
        user_bookmark.append(mitra_id)
    user["bookmark_mitra"] = user_bookmark
    update, err = db.update_one(USER_COLLECTION, {"_id": user.get("_id")}, user)
    if err:
        flash(err, "error")
        return redirect(url_for("user_mitra"))

    flash("Berhasil membuat bookmark", "success")
    return redirect(url_for("user_mitra"))
