import os

from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "local-only-key"),
        MAX_CONTENT_LENGTH=32 * 1024,
    )
    if test_config is not None:
        app.config.update(test_config)

    from .main.routes import main_bp
    app.register_blueprint(main_bp)

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
        )
        return response

    @app.errorhandler(413)
    def request_too_large(_error):
        return render_template("error.html", message="A requisição é muito grande."), 413

    return app
