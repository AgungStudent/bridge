from datetime import datetime
from math import atan2, cos, radians, sin, sqrt

from bson.son import SON
from flask import flash, redirect, request, url_for

from config import (CLAIM_COLLECTION, FOOD_COLLECTION, MITRA_COLLECTION,
                    USER_COLLECTION)
from model import db


def generate_token(user):
    user["tokenApply"] = db.randomStr(6)
    user, err = db.update_one(USER_COLLECTION, {"_id": user.get("_id")}, user)
    if err:
        flash(err, "error")
        return redirect(url_for("user_index"))
    flash("berhasil membuat token", "success")
    return redirect(url_for("user_index"))


def get_user_histories(user):

    pipeline = [
        {
            "$lookup": {
                "from": "foods",
                "localField": "foodId",
                "foreignField": "_id",
                "as": "foods",
            }
        },
        {
            "$project": {
                "_id": 1,
                "userName": 1,
                "quantity": 1,
                "point": 1,
                "claimAt": 1,
                "foods": {"name": 1},
            }
        },
    ]

    mitra_collection = db.get_db()[CLAIM_COLLECTION]
    result = list(mitra_collection.aggregate(pipeline))

    return result


def get_user_mitra_map(user):
    mitra_list = []
    search = request.args.get("search", "")

    mitras, err = db.find(
        MITRA_COLLECTION, {"name": {"$regex": search, "$options": "i"}}
    )

    if mitras is None:
        return mitra_list
    for mitra in mitras:
        mitra_list.append(
            {
                "lat": mitra.get("lat"),
                "lon": mitra.get("lon"),
                "label": mitra.get("name"),
            }
        )
    return mitra_list


def get_user_mitra(user):
    user_lat = float(user["lat"])
    user_lon = float(user["lon"])
    mitra_list = []
    search = request.args.get("search", "")

    pipeline = [
        {
            "$lookup": {
                "from": "foods",
                "localField": "_id",
                "foreignField": "mitra_id",
                "as": "foods",
            }
        },
        {"$match": {"name": {"$regex": search, "$options": "i"}}},
        {"$project": {"_id": 1, "name": 1, "foods": 1}},
    ]

    mitra_collection = db.get_db()[MITRA_COLLECTION]
    result = list(mitra_collection.aggregate(pipeline))

    mitra, err = db.find(
        MITRA_COLLECTION, {"name": {"$regex": search, "$options": "i"}}
    )
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
        mitra_point["foods"] = next(
            (mitra["foods"] for mitra in result if mitra["_id"] == mitra_point["_id"]),
            [],
        )
        mitra_list.append(mitra_point)
    mitra_list.sort(key=lambda x: x["distance"])
    # mitra, err = db.find_one(MITRA_COLLECTION, {})
    return mitra_list


def get_user_mitra_bookmark(user):
    user_lat = float(user["lat"])
    user_lon = float(user["lon"])
    mitra_list = []
    bookmark_mitra_ids = user.get("bookmark_mitra", [])
    search = request.args.get("search", "")

    pipeline = [
        {
            "$match": {
                "_id": {"$in": bookmark_mitra_ids},
                "name": {"$regex": search, "$options": "i"},
            }
        },
        {
            "$lookup": {
                "from": "foods",
                "localField": "_id",
                "foreignField": "mitra_id",
                "as": "foods",
            }
        },
        {"$project": {"_id": 1, "name": 1, "foods": 1}},
    ]

    mitra_collection = db.get_db()[MITRA_COLLECTION]
    result = list(mitra_collection.aggregate(pipeline))

    mitra, err = db.find(
        MITRA_COLLECTION,
        {
            "_id": {"$in": bookmark_mitra_ids},
            "name": {"$regex": search, "$options": "i"},
        },
    )
    if mitra is None:
        return mitra_list
    for mitra_point in mitra:
        mitra_lat = float(mitra_point["lat"])
        mitra_lon = float(mitra_point["lon"])
        distance = calculate_distance(user_lat, user_lon, mitra_lat, mitra_lon)
        mitra_point["map_link"] = (
            f"https://www.google.com/maps?q={mitra_lat},{mitra_lon}&z=17&hl=en"
        )
        mitra_point["distance"] = distance
        mitra_point["foods"] = next(
            (mitra["foods"] for mitra in result if mitra["_id"] == mitra_point["_id"]),
            [],
        )
        mitra_list.append(mitra_point)
    mitra_list.sort(key=lambda x: x["distance"])
    return mitra_list


def get_user_products(user):
    # TODO: need to test
    foods, err = db.find(
        FOOD_COLLECTION, {"stock": {"$gt": 0}, "expiredAt": {"$gte": datetime.now()}}
    )
    return foods


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
