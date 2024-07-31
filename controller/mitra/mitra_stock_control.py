from datetime import datetime

from apn_validators import validate
from flask import flash, redirect, render_template, request, session, url_for
from flask_mailman import EmailMessage, Mail

from config import (CLAIM_COLLECTION, FOOD_COLLECTION, MITRA_COLLECTION,
                    USER_COLLECTION)
from model import db
from schema.rules import (DateAfter, GreaterThenOrEqual, Length,
                          LessThenOrEqual, NotBlank)
from schema.UniqueRule import ExistsRule


def validate_save_stock(data, is_update=False):
    schema = {
        "name": [NotBlank(), Length(3, 50)],
        "price": [NotBlank(), GreaterThenOrEqual(0), LessThenOrEqual(50)],
        "stock": [NotBlank(), GreaterThenOrEqual(1)],
        "expiredAt": [NotBlank()],
    }
    if is_update:
        schema["_id"] = [NotBlank(), ExistsRule(FOOD_COLLECTION, "_id")]
    return validate(schema, data, is_err_to_list=True)


def validate_update_stock(data, is_update=False):
    schema = {
        "_id": [NotBlank()],
        "name": [NotBlank(), Length(3, 50)],
        "price": [NotBlank(), GreaterThenOrEqual(0), LessThenOrEqual(100)],
        "stock": [NotBlank(), GreaterThenOrEqual(1)],
        "expiredAt": [NotBlank()],
    }
    if is_update:
        schema["_id"] = [NotBlank(), ExistsRule(FOOD_COLLECTION, "_id")]
    return validate(schema, data, is_err_to_list=True)


def validate_redeem(data):
    return validate(
        {
            "_id": [NotBlank(), ExistsRule(FOOD_COLLECTION, "_id")],
            "quantity": [NotBlank(), GreaterThenOrEqual(1)],
            "token": [NotBlank(), ExistsRule(USER_COLLECTION, "tokenApply")],
        },
        data,
        is_err_to_list=True,
    )


def get_stocks():
    mitraId = session.get("mitra_id")
    data, err = db.find(FOOD_COLLECTION, {"mitra_id": mitraId})
    mitras = ''
    if data[0].get("parentId") == None:
        mitras = "parent"

    if err:
        flash(err)
        return redirect(url_for("mitra_stock"))
    return render_template("/mitra/mitra-stock.html", data=data, is_mitra=mitraId, mitra=mitras)


def create():
    mitraId = session.get("mitra_id")
    data, err = validate_save_stock(request.form.to_dict())
    users, err = db.find(USER_COLLECTION, {"bookmark_mitra": mitraId})
    mitra, err = db.find(MITRA_COLLECTION, {"_id": mitraId})
    userList = []
    for user in users:
        userList.append(user["email"])
    print(userList)
    # kurang looping user e men entok kabeh email
    msg = EmailMessage(
        "Password Reset",
        f"Mitra {mitra[0]["name"]} telah menambah menu baru, segera login untuk menukar makanan dengan poin",
        "foodbridge@fastmail.com",
        userList,
    )
    msg.send()

    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("mitra_stock"))

    data["mitra_id"] = mitraId
    data["claims"] = []
    data["endAt"] = db.startOfDay(1)  # expired tomorrow
    food, err = db.insert_one(FOOD_COLLECTION, data)
    if err:
        flash(err, "error")
        return redirect(url_for("mitra_stock"))

    flash("berhasil menambahkan stok makanan", "success")
    return redirect(url_for("mitra_stock"))


def update():
    data, err = validate_update_stock(request.form.to_dict())
    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("mitra_stock"))

    food, err = db.update_one(FOOD_COLLECTION, {"_id": data["_id"]}, data)

    if err:
        flash(err, "error")
        return redirect(url_for("mitra_stock"))

    flash("berhasil merubah stok makanan", "success")
    return redirect(url_for("mitra_stock"))


def delete():
    food, err = db.delete_one(FOOD_COLLECTION, {"_id": request.form.get("_id")})
    if err:
        flash(err, "error")
        return redirect(url_for("mitra_stock"))

    flash("berhasil menghapus stok makanan", "success")
    return redirect(url_for("mitra_stock"))


def redeem():
    data, err = validate_redeem(request.form.to_dict())
    if err:
        db.list_to_flash(err, "error")
        return redirect(url_for("mitra_stock"))
    user, err = db.find_one(USER_COLLECTION, {"tokenApply": data.get("token")})
    food, err = db.find_one(FOOD_COLLECTION, {"_id": data.get("_id")})
    total_price = int(data.get("quantity", 1)) * int(food.get("price"))
    balance_shift = int(user.get("balance")) - total_price
    if balance_shift < 0:
        flash("balance tidak cukup", "error")
        return redirect(url_for("mitra_stock"))
    result, err = db.update_one(
        USER_COLLECTION,
        {"_id": user.get("_id")},
        {"balance": balance_shift, "tokenApply": ""},
    )
    if err:
        flash(err, "error")
        return redirect(url_for("mitra_stock"))

    transaksi = {
                    "userId": user.get("_id"),
                    "userName": user.get("name"),
                    "quantity": data.get("quantity"),
                    "point": total_price,
                    "claimAt": datetime.now(),
                    'foodId': food.get('_id'),
                    'mitraId':food.get('mitra_id')
                }

    food, err = db.update_one_default(
        FOOD_COLLECTION,
        {"_id": food.get("_id")},
        {
            "$push": {
                "claims": transaksi
            }
        },
    )
    transaksi, err = db.insert_one(CLAIM_COLLECTION,transaksi)    
    if err:
        flash(err, "error")
        return redirect(url_for("mitra_stock"))
    flash("berhasil redeem", "success")
    return redirect(url_for("mitra_stock"))
