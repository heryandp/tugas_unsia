import os
import inspect

from werkzeug.wrappers import Response
from flask_sock import Sock

from flask import Flask
from flask_smorest import Api

from .config import Config
from .db import init_app as init_db_app, init_db
from .errors import register_errors


def _ensure_partitioned_cookie_support():
    sig = inspect.signature(Response.set_cookie)
    if "partitioned" not in sig.parameters:
        original = Response.set_cookie

        def patched_set_cookie(
            self,
            key,
            value="",
            max_age=None,
            expires=None,
            path="/",
            domain=None,
            secure=False,
            httponly=False,
            samesite=None,
            partitioned=False,
        ):
            return original(self, key, value, max_age, expires, path, domain, secure, httponly, samesite)

        Response.set_cookie = patched_set_cookie


sock = Sock()


def create_app():
    _ensure_partitioned_cookie_support()

    # Determine the project root directory strictly based on this file's location
    # f:/Dit IP/sistem-pa/app/__init__.py -> f:/Dit IP/sistem-pa/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
        static_url_path="/static",
    )
    app.config.from_object(Config)

    # Ensure uploads directory exists
    upload_folder = app.config["UPLOAD_FOLDER"]
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)

    init_db_app(app)
    with app.app_context():
        init_db()

    from .blueprints.public import bp as public_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.dashboard import bp as dashboard_bp
    from .blueprints.admin import bp as admin_bp
    from .blueprints.export import bp as export_bp
    from .blueprints.uploads import bp as uploads_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(uploads_bp)

    register_errors(app)

    @app.after_request
    def apply_security_headers(resp):
        csp = "; ".join(
            [
                f"default-src {app.config['CSP_DEFAULT_SRC']}",
                f"img-src {app.config['CSP_IMG_SRC']}",
                f"style-src {app.config['CSP_STYLE_SRC']}",
                f"script-src {app.config['CSP_SCRIPT_SRC']}",
                f"font-src {app.config['CSP_FONT_SRC']}",
                f"connect-src {app.config['CSP_CONNECT_SRC']}",
                "frame-ancestors 'none'",
            ]
        )
        resp.headers.setdefault("Content-Security-Policy", csp)
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        return resp

    api = Api(app)
    from .api import register_api
    register_api(api)

    sock.init_app(app)
    # Register WebSocket routes
    from . import ws  # noqa: F401
    return app
