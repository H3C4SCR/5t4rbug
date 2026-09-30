from pathlib import Path

from flask import Flask, g, render_template

from .config import Config
from .db import close_db, init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if app.config.get("DATABASE") is None:
        app.config["DATABASE"] = Path(app.instance_path) / "5t4rbug.sqlite3"
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(close_db)

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .auth.service import load_current_user

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.before_request
    def before_request():
        load_current_user()
        if not request_has_csrf_cookie():
            g.new_csrf_token = __import__("secrets").token_urlsafe(32)

    @app.after_request
    def after_request(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
        )
        if getattr(g, "new_csrf_token", None):
            response.set_cookie(
                "5t4rbug_csrf",
                g.new_csrf_token,
                max_age=app.config["SESSION_MAX_AGE"],
                secure=app.config["SESSION_COOKIE_SECURE"],
                httponly=False,
                samesite="Lax",
            )
        return response

    @app.context_processor
    def inject_template_helpers():
        from .auth.service import csrf_token
        return {"csrf_token": csrf_token, "current_user": g.get("user")}

    @app.errorhandler(413)
    def request_too_large(_error):
        return render_template("error.html", message="A requisição é muito grande."), 413

    with app.app_context():
        init_db()

    return app


def request_has_csrf_cookie():
    from flask import request
    return bool(request.cookies.get("5t4rbug_csrf"))
