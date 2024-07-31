from functools import wraps

from flask import flash, redirect, session, url_for

from config import MITRA_COLLECTION, USER_COLLECTION
from model import db


def user(role="user"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("user_id") is not None:
                data, _ = db.find_one(USER_COLLECTION, {"_id": session.get("user_id")})
                if data.get("role") == "admin":
                    return f(*args, **kwargs)

                if data.get("status") == "APPROVE":
                    if data is not None:
                        if data.get("role") == role:
                            return f(*args, **kwargs)
                        flash("tidak punya akses")
                        return redirect(url_for("user_index"))
            return redirect(url_for("user_sign_in"))

        return decorated_function

    return decorator


def mitra(role=None):
    """
    set to empty if feature doesn't care about role
    set to 'mitra' if feature only can access by mitra
    set to 'branch' if feature only can access by branch mitra
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("mitra_id") is not None:
                data, _ = db.find_one(
                    MITRA_COLLECTION, {"_id": session.get("mitra_id")}
                )
                print(session.get("mitra_id"))
                if data is not None:
                    if role is None:
                        return f(*args, **kwargs)
                    elif role == "mitra" and data.get("parentId") is None:
                        return f(*args, **kwargs)
                    elif role == "branch" and data.get("parentId") is not None:
                        return f(*args, **kwargs)
                    flash("tidak punya akses")
                    return redirect(url_for("user_index"))
            return redirect(url_for("user_sign_in"))

        return decorated_function

    return decorator
