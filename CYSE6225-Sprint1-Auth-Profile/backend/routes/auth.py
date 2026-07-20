from flask import Blueprint, request, jsonify
from botocore.exceptions import ClientError

from models import user as user_model
from utils.validators import is_valid_email, is_valid_password
from utils.auth_helpers import generate_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    nickname = (data.get("nickname") or "").strip()

    if not is_valid_email(email):
        return jsonify({"error": "Please provide a valid email address"}), 400
    if not is_valid_password(password):
        return jsonify({"error": "Password must be at least 8 characters and include letters and numbers"}), 400
    if user_model.get_user_by_email(email):
        return jsonify({"error": "An account with this email already exists"}), 409

    try:
        new_user = user_model.create_user(email, password, nickname)
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

    token = generate_token(new_user["user_id"], new_user["email"])
    return jsonify({"token": token, "user": user_model.public_user(new_user)}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    existing = user_model.get_user_by_email(email)
    if not existing or not user_model.verify_password(existing, password):
        return jsonify({"error": "Incorrect email or password"}), 401

    token = generate_token(existing["user_id"], existing["email"])
    return jsonify({"token": token, "user": user_model.public_user(existing)}), 200
