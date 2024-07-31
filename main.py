import json

from flask import Flask, redirect, render_template, request, session, url_for
from flask_apscheduler import APScheduler
from flask_mailman import Mail

import autorize
from controller.admin import admin_pages
from controller.mitra import (
    mitra_auth,
    mitra_branch,
    mitra_history,
    mitra_mail,
    mitra_stock_control,
)
from controller.user import auth, user_bookmark, user_mail, user_pages
from model.db import user_signed

app = Flask(__name__)
app.config["SECRET_KEY"] = "ABCDEFGHIJK"
mail = Mail()
app.config["MAIL_SERVER"] = "smtp.fastmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "foodbridge@fastmail.com"
app.config["MAIL_PASSWORD"] = "8z3e5x237b2x2z2t"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

# app.config["MAIL_SERVER"] = "smtp.gmail.com"
# app.config["MAIL_PORT"] = 587
# app.config["MAIL_USERNAME"] = "agungpn33@gmail.com"
# app.config["MAIL_PASSWORD"] = "zcsp abak chja aybp"
# app.config["MAIL_USE_TLS"] = True
# app.config["MAIL_USE_SSL"] = False
mail.init_app(app)


schaduler = APScheduler()
schaduler.api_enabled = True
schaduler.init_app(app)

@app.route("/")
def index():
    return render_template("/index.html")


# ===========================
# MITRA
# ===========================
# mail
@app.route("/mitra/forgot-password", methods=["GET", "POST"])
def mitra_forgot_password():
    if request.method == "GET":
        return render_template("/mitra/mitra-forgot-password.html")
    return mitra_mail.send_mail()


@app.route("/mitra/reset-password/<token>", methods=["GET", "POST"])
def mitra_reset_password(token):
    if request.method == "GET":
        return render_template("/mitra/mitra-reset-password.html", token=token)
    return mitra_mail.reset_password(token)


# AUTH
# ===========================
@app.route("/mitra/sign-in", methods=["GET", "POST"])
def mitra_sign_in():
    if request.method == "GET":
        return render_template("/mitra/mitra-signin.html")
    return mitra_auth.mitra_sign_in()


@app.route("/mitra/sign-up", methods=["GET", "POST"])
def mitra_sign_up():
    if request.method == "GET":
        return render_template("/mitra/mitra-signup.html")
    return mitra_auth.mitra_sign_up()


@app.route("/mitra/sign-out", methods=["GET", "POST"])
def mitra_sign_out():
    if session.get("mitra_id"):
        session.pop("mitra_id")
    return redirect(url_for("mitra_sign_in"))


# BRANCH
# ===========================
@app.route("/mitra/branch", methods=["GET", "POST"])
@autorize.mitra()
def manage_mitra_branch():
    if request.method == "GET":
        mitraBranch = mitra_branch.get_branch()
        return render_template("/mitra/mitra-branch.html", data=mitraBranch)
    return mitra_branch.add_branch()


@app.route("/mitra/branch/delete", methods=["GET", "POST"])
@autorize.mitra("mitra")
def delete_mitra_branch():
    return mitra_branch.delete_branch()


@app.route("/mitra/branch/update", methods=["GET", "POST"])
@autorize.mitra("mitra")
def update_mitra_branch():
    return mitra_branch.update_branch()


# STOCk
# ===========================
@app.route("/mitra/stock", methods=["GET", "POST"])
@autorize.mitra()
def mitra_stock():
    if request.method == "GET":
        return mitra_stock_control.get_stocks()

    return mitra_stock_control.create()


@app.post("/mitra/stock/update")
@autorize.mitra()
def mitra_stock_update():
    return mitra_stock_control.update()


@app.post("/mitra/stock/delete")
@autorize.mitra()
def mitra_stock_delete():
    return mitra_stock_control.delete()


@app.post("/mitra/stock/redeem")
@autorize.mitra()
def mitra_stock_redeem():
    return mitra_stock_control.redeem()


@app.route("/mitra/history")
@autorize.mitra()
def mitra_histories():
    data = mitra_history.history()
    return render_template("/mitra/mitra-history.html", data=data)


# ====================
# USER
# ====================

@app.route("/user/sign-out", methods=["GET", "POST"])
def user_sign_out():
    if session.get("user_id"):
        session.pop("user_id")
    return redirect(url_for("user_sign_in"))

@app.route("/user/sign-up", methods=["GET", "POST"])
def user_sign_up():
    if request.method == "GET":
        # TODO: Belum ada FE page
        return render_template("/user/user-signup.html")
    return auth.user_sign_up()


@app.route("/user/sign-in", methods=["GET", "POST"])
def user_sign_in():
    if request.method == "GET":
        return render_template("/user/user-signin.html")
    return auth.user_sign_in()


@app.route("/user/verif")
def user_verif():
    status = session["status"]
    return render_template("/user/user-verif.html", status=status)


# mail
@app.route("/user/forgot-password", methods=["GET", "POST"])
def user_forgot_password():
    if request.method == "GET":
        return render_template("/user/user-forgot-password.html")
    return user_mail.send_mail()


@app.route("/user/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "GET":
        return render_template("/user/user-reset-password.html", token=token)
    return user_mail.reset_password(token)


@app.route("/user/history")
@autorize.user()
def user_histories():
    user = user_signed()
    data = user_pages.get_user_histories(user)
    return render_template("/user/user-history.html", data=data, user=user)


@app.route("/user/mitra")
@autorize.user()
def user_mitra():
    user = user_signed()
    data = user_pages.get_user_mitra(user)
    print(
        data[0].get("_id") in user.get("bookmark_mitra"),
        user.get("bookmark_mitra"),
        data[0].get("_id"),
    )
    return render_template("/user/user-mitra.html", data=data, user=user)


@app.route("/user/mitra/bookmark")
@autorize.user()
def user_mitra_bookmark():
    user = user_signed()
    data = user_pages.get_user_mitra_bookmark(user)
    return render_template("/user/user-mitra-bookmark.html", data=data, user=user)


@app.route("/user/mitra/bookmark/toggle")
@autorize.user()
def user_mitra_toggle_bookmark():
    return user_bookmark.add_bookmark()


@app.route("/user/mitra/map")
@autorize.user()
def user_mitra_map():
    user = user_signed()
    data = user_pages.get_user_mitra_map(user)
    return render_template(
        "/user/user-mitra-map.html", data=json.dumps(data), user=user
    )


@app.route("/user/products")
@autorize.user()
def user_products():
    data = user_pages.get_user_products(user_signed())
    return render_template("/user/user-products.html", data=data)


@app.route("/user")
@autorize.user()
def user_index():
    # cuma buat ngarahin ke histories sih, tapi gk usah dihapus. kecuali semua 'user_index' dirubah
    return redirect(url_for("user_histories"))


@app.route("/user/profile")
@autorize.user()
def user_profile():
    user = auth.user_profile()
    return render_template("user/user-profile", user=user)


@app.post("/user/token")
@autorize.user()
def user_token_generate():
    return user_pages.generate_token(user_signed())


# ====================
# admin
# ====================


@app.route("/admin/sign-in", methods=["GET", "POST"])
def admin_sign_in():
    if request.method == "GET":
        return render_template("/admin/admin-signin.html")
    return admin_pages.admin_sign_in()


@app.route("/admin/confirm/user", methods=["GET", "POST"])
@autorize.user("admin")
def admin_confirm_user():
    if request.method == "GET":
        users = admin_pages.get_confirm_user()
        return render_template("/admin/admin-verify-user.html", users=users)
    return admin_pages.admin_confirm_user()


@app.route("/admin/sign-out", methods=["GET", "POST"])
def admin_sign_out():
    if session.get("user_id"):
        session.pop("user_id")
    return redirect(url_for("admin_sign_in"))


@app.route("/admin/confirm/mitra", methods=["GET", "POST"])
def admin_confirm_mitra():
    if request.method == "GET":
        admin_pages.get_confirm_admin()
    return admin_pages.admin_confirm_mitra()


# Task Schaduler
# @schaduler.task("cron", id="reset_user_balance", hour=0, minute=0)
# def schadule_reset_user_balance():
#     user_apply.schadule_generate_token()


app.run(port=8080, debug=True)
