import os
from decimal import Decimal

from flask import Flask, send_from_directory
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import Config
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.videos import videos_bp
from routes.search import search_bp
from routes.ratings import ratings_bp
from routes.comments import comments_bp
from routes.favorites import favorites_bp
from routes.history import history_bp
from routes.reports import reports_bp


# Static frontend lives one level up from backend/ (see repo layout).
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


def _json_default(obj):
    """DynamoDB returns every number as a `Decimal`, which Flask's stock JSON
    encoder cannot serialize (it raises TypeError -> 500). Convert Decimals to
    int when whole, otherwise float; delegate everything else to the default.
    Installed on the app's JSON provider so it applies across ALL endpoints."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return DefaultJSONProvider.default(obj)


def create_app():
    # static_url_path="" serves the frontend at the site root, so /css/style.css,
    # /js/api.js, /index.html, etc. resolve directly.
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
    app.config.from_object(Config)
    app.json.default = _json_default  # handle DynamoDB Decimals everywhere

    # Auth is via `Authorization: Bearer <token>` (not cookies), so we don't
    # need credentialed CORS. (origins="*" + credentials is an invalid combo.)
    CORS(app, origins=Config.CORS_ORIGINS)

    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

    @app.get("/api/uploads/avatars/<path:filename>")
    def serve_avatar(filename):
        return send_from_directory(Config.UPLOAD_DIR, filename)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(videos_bp, url_prefix="/api/videos")
    app.register_blueprint(search_bp, url_prefix="/api/search")
    app.register_blueprint(ratings_bp, url_prefix="/api/videos")
    app.register_blueprint(comments_bp, url_prefix="/api/videos")
    app.register_blueprint(favorites_bp, url_prefix="/api/favorites")
    app.register_blueprint(history_bp, url_prefix="/api/history")
    app.register_blueprint(reports_bp, url_prefix="/api/videos")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/")
    def index():
        # First page the user sees is the login / register page.
        return send_from_directory(FRONTEND_DIR, "login.html")

    @app.errorhandler(Exception)
    def handle_uncaught(err):
        # Let normal HTTP errors (404, 401, ...) pass through untouched.
        if isinstance(err, HTTPException):
            return err
        app.logger.exception("Unhandled error")
        return {"error": "Internal server error"}, 500

    return app


# `flask --app app run` looks for a module-level `app` or `create_app`
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=True)
