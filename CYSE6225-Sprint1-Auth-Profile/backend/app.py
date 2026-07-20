"""Sprint 1 subset: only the Auth and Profile blueprints are wired up here.
The full project's app.py (see the main repo) also registers videos, search,
ratings, comments, favorites, history, and reports -- add those back in as
later sprints land."""
from flask import Flask
from flask_cors import CORS

from config import Config
from routes.auth import auth_bp
from routes.profile import profile_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
