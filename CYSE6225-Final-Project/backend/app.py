from flask import Flask
from flask_cors import CORS

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


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

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

    return app


# `flask --app app run` looks for a module-level `app` or `create_app`
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.__dict__.get("PORT", 5000), debug=True)
