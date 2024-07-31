from datetime import datetime

import bcrypt
from apn_validators import validate
from flask import flash, jsonify, redirect, request, session, url_for

from config import MITRA_COLLECTION
from model import db
from schema.rules import Length, NotBlank, Password
from schema.UniqueRule import UniqueRule


def validate_new_branch(data):
    return validate(
        {
            "email": [NotBlank(), UniqueRule(MITRA_COLLECTION, "email")],
            "password": [NotBlank(), Password()],
            "name": [NotBlank(), Length(4, 50)],
            "city": [NotBlank()],
            "address": [NotBlank()],
            "lat": [NotBlank()],
            "lon": [NotBlank()],
        },
        data,
        is_err_to_list=True,
    )

def validate_update_branch(data):
    return validate(
        {
            "_id": [NotBlank()],
            "email": [NotBlank(), UniqueRule(MITRA_COLLECTION, "email")],
            "name": [NotBlank(), Length(4, 50)],
            "city": [NotBlank()],
            "address": [NotBlank()],
            "lat": [NotBlank()],
            "lon": [NotBlank()],
        },
        data,
        is_err_to_list=True,
    )

def get_branch():
    mitraParent = session['mitra_id']
    mitraList,err = db.find(MITRA_COLLECTION, {"parentId": mitraParent})
    return mitraList

def add_branch():
    data, err = validate_new_branch(request.form.to_dict())
    if err:
        return jsonify({"errors": err}), 400

    data["password"] = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())

    data["parentId"] = session['mitra_id']
    data["verifyAt"] = datetime.now()
    data["foods"] = []

    _, err = db.insert_one(MITRA_COLLECTION, data)
    if err:
        flash(err)
        return redirect(url_for("manage_mitra_branch"))

    return redirect(url_for("manage_mitra_branch"))

def update_branch():
    data, err = validate_update_branch(request.form.to_dict())
    print(data)
    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("manage_mitra_branch"))
    branch, err = db.update_one(MITRA_COLLECTION, {"_id": data["_id"]}, data)
    if err:
        flash(err, "error")
        return redirect(url_for("manage_mitra_branch"))

    flash("berhasil merubah cabang", "success")
    return redirect(url_for("manage_mitra_branch"))

def delete_branch():
    branch, err = db.delete_one(MITRA_COLLECTION, {"_id": request.form.get("_id")})
    if err:
        flash(err, "error")
        return redirect(url_for("mitra_stock"))

    flash("berhasil menghapus cabang", "success")
    return redirect(url_for("manage_mitra_branch"))
