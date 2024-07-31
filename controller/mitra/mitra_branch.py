from datetime import datetime
from math import atan2, cos, radians, sin, sqrt

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
            "email": [NotBlank()],
            "name": [NotBlank(), Length(4, 50)],
            "city": [NotBlank()],
            "address": [NotBlank()],
            "lat": [NotBlank()],
            "lon": [NotBlank()],
        },
        data,
        is_err_to_list=True,
    )


def get_branch(user):
    mitra_parent_id = session["mitra_id"]
    mitra, err = db.find(MITRA_COLLECTION, {"parentId": mitra_parent_id})
    print(mitra)
    user_lat = float(user["lat"])
    user_lon = float(user["lon"])
    mitra_list = []
    if mitra is None:
        return mitra_list
    for mitra_point in mitra:
        mitra_lat = float(mitra_point["lat"])
        mitra_lon = float(mitra_point["lon"])
        distance = calculate_distance(user_lat, user_lon, mitra_lat, mitra_lon)
        mitra_point["distance"] = distance
        mitra_point["map_link"] = (
            f"https://www.google.com/maps?q={mitra_lat},{mitra_lon}&z=17&hl=en"
        )
        mitra_list.append(mitra_point)
    mitra_list.sort(key=lambda x: x["distance"])
    print(mitra_list)

    return mitra_list


def get_one():
    mitra_id = request.args.get("id")
    mitra, err = db.find(MITRA_COLLECTION, {"_id": mitra_id})
    if mitra is None:
        flash("mitra tidak ditemukkan", "error")
        return redirect(url_for("manage_mitra_branch"))
    return mitra


def add_branch():
    data, err = validate_new_branch(request.form.to_dict())
    if err:
        return jsonify({"errors": err}), 400

    data["password"] = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())

    data["parentId"] = session["mitra_id"]
    data["verifyAt"] = datetime.now()
    data["foods"] = []

    _, err = db.insert_one(MITRA_COLLECTION, data)
    if err:
        flash(err)
        return redirect(url_for("manage_mitra_branch"))

    flash("berhasil membuat cabang", "success")
    return redirect(url_for("manage_mitra_branch"))


def update_branch():
    data, err = validate_update_branch(request.form.to_dict())
    __import__("pprint").pprint(request.form.to_dict())
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


def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate the distance between two points on the earth
    R = 6371.0  # Earth radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance
