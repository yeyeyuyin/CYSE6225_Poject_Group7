"""JWT issuing/verification + a require_auth decorator for protected routes."""
import datetime
import functools

import jwt
from flask import request, jsonify, g

from config import Config


def generate_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=Config.JWT_EXPIRES_HOURS),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])


def require_auth(fn):
    """Decorator: rejects the request unless a valid Bearer token is present.
    On success, sets g.user_id / g.user_email for the view to use."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        g.user_id = payload["sub"]
        g.user_email = payload["email"]
        return fn(*args, **kwargs)

    return wrapper


def optional_auth(fn):
    """Like require_auth but doesn't fail when there's no token — useful for
    routes like comment listing that are public but personalize when logged in."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        g.user_id = None
        g.user_email = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            try:
                payload = decode_token(token)
                g.user_id = payload["sub"]
                g.user_email = payload["email"]
            except jwt.InvalidTokenError:
                pass
        return fn(*args, **kwargs)

    return wrapper
