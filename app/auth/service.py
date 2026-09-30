import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from flask import current_app, g, request
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db


def normalize_email(email):
    return email.strip().lower()


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_password(password):
    return generate_password_hash(password, method="scrypt")


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def create_session(user_id):
    session_token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=current_app.config["SESSION_MAX_AGE"])
    db = get_db()
    db.execute(
        "INSERT INTO sessions (token_hash, user_id, csrf_hash, expires_at) VALUES (?, ?, ?, ?)",
        (hash_token(session_token), user_id, hash_token(csrf), expires_at.isoformat()),
    )
    db.commit()
    return session_token, csrf


def revoke_session(session_token):
    if session_token:
        db = get_db()
        db.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(session_token),))
        db.commit()


def load_current_user():
    g.user = None
    g.session = None
    token = request.cookies.get(current_app.config["AUTH_COOKIE_NAME"])
    if not token:
        return

    db = get_db()
    session = db.execute(
        """
        SELECT sessions.token_hash, sessions.csrf_hash, sessions.expires_at,
               users.id, users.email
        FROM sessions JOIN users ON users.id = sessions.user_id
        WHERE sessions.token_hash = ?
        """,
        (hash_token(token),),
    ).fetchone()

    if session is None:
        return

    expires_at = datetime.fromisoformat(session["expires_at"])
    if expires_at <= datetime.now(timezone.utc):
        revoke_session(token)
        return

    g.user = {"id": session["id"], "email": session["email"]}
    g.session = {
        "token": token,
        "token_hash": session["token_hash"],
        "csrf_hash": session["csrf_hash"],
    }


def csrf_token():
    return request.cookies.get("5t4rbug_csrf") or getattr(g, "new_csrf_token", "")


def validate_csrf():
    submitted = request.form.get("csrf_token", "")
    cookie_value = request.cookies.get("5t4rbug_csrf", "")
    if not submitted or not cookie_value or not hmac.compare_digest(submitted, cookie_value):
        return False
    if g.session:
        return hmac.compare_digest(hash_token(submitted), g.session["csrf_hash"])
    return True
