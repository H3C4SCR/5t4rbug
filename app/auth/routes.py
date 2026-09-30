import re

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import BadRequest

from ..db import get_db
from .service import (
    create_session,
    hash_password,
    normalize_email,
    revoke_session,
    validate_csrf,
    verify_password,
)


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def set_session_cookie(response, token, csrf):
    response.set_cookie(
        current_app.config["AUTH_COOKIE_NAME"],
        token,
        max_age=current_app.config["SESSION_MAX_AGE"],
        secure=current_app.config["SESSION_COOKIE_SECURE"],
        httponly=True,
        samesite="Lax",
        path="/",
    )
    response.set_cookie(
        "5t4rbug_csrf",
        csrf,
        max_age=current_app.config["SESSION_MAX_AGE"],
        secure=current_app.config["SESSION_COOKIE_SECURE"],
        httponly=False,
        samesite="Lax",
        path="/",
    )
    return response


def clear_session_cookie(response):
    response.delete_cookie(current_app.config["AUTH_COOKIE_NAME"], path="/")
    response.delete_cookie("5t4rbug_csrf", path="/")
    return response


def reject_invalid_csrf():
    if not validate_csrf():
        raise BadRequest("Token CSRF inválido.")


@auth_bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        reject_invalid_csrf()
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
            flash("Informe um e-mail válido.", "error")
        elif len(password) < 12:
            flash("A senha precisa ter pelo menos 12 caracteres.", "error")
        elif password != confirmation:
            flash("As senhas não coincidem.", "error")
        else:
            db = get_db()
            try:
                cursor = db.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    (email, hash_password(password)),
                )
                db.commit()
            except Exception as error:
                db.rollback()
                if "UNIQUE constraint failed" in str(error):
                    flash("Não foi possível criar a conta com esses dados.", "error")
                else:
                    raise
            else:
                token, csrf = create_session(cursor.lastrowid)
                response = redirect(url_for("main.dashboard"))
                return set_session_cookie(response, token, csrf)

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        reject_invalid_csrf()
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user is None or not verify_password(user["password_hash"], password):
            flash("E-mail ou senha inválidos.", "error")
        else:
            token, csrf = create_session(user["id"])
            response = redirect(url_for("main.dashboard"))
            return set_session_cookie(response, token, csrf)

    return render_template("auth/login.html")


@auth_bp.post("/logout")
def logout():
    reject_invalid_csrf()
    token = request.cookies.get(current_app.config["AUTH_COOKIE_NAME"])
    revoke_session(token)
    response = redirect(url_for("auth.login"))
    return clear_session_cookie(response)
