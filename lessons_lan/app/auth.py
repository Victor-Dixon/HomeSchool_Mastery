"""
Project: Homeschool Lessons (Dream.OS)
File: app/auth.py
Purpose: Authentication helpers (login/logout, session guards).
Owner: Local family deployment (homeschool)
"""

from functools import wraps

from flask import g, redirect, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db


def load_logged_in_user():
    """
    Attach the current user to g. If the session points at a missing user (e.g. after reset-db),
    clear the session so we redirect to login instead of 500ing on g.user['id'].

    Any DB error here (locked DB, bad path) must not bubble — that would 500 every request with a cookie.
    """
    g.user = None
    user_id = session.get("user_id")
    if user_id is None:
        return
    try:
        row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    except Exception:
        session.clear()
        return
    if row is None:
        session.clear()
        return
    g.user = row


def login(username: str, password: str):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username.lower(),)).fetchone()
    if user is None:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    session.clear()
    session["user_id"] = user["id"]
    return user


def logout():
    session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None or g.user is None:
            return redirect(url_for("routes.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None or g.user is None:
            return redirect(url_for("routes.login", next=request.path))
        if g.user["is_admin"] != 1:
            return redirect(url_for("routes.today"))
        return view(*args, **kwargs)

    return wrapped

