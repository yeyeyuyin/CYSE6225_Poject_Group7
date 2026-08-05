from flask import Blueprint, request, jsonify, g

from models import user as user_model
from utils.auth_helpers import require_auth
from utils.validators import is_valid_password

profile_bp = Blueprint("profile", __name__)


@profile_bp.get("/me")
@require_auth
def get_me():
    u = user_model.get_user_by_id(g.user_id)
    if not u:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_model.public_user(u))


@profile_bp.put("/me")
@require_auth
def update_me():
    data = request.get_json(silent=True) or {}
    nickname = data.get("nickname")
    avatar_url = data.get("avatar_url")
    updated = user_model.update_profile(g.user_id, nickname=nickname, avatar_url=avatar_url)
    return jsonify(user_model.public_user(updated))


@profile_bp.put("/me/password")
@require_auth
def change_password():
    data = request.get_json(silent=True) or {}
    old_password = data.get("old_password") or ""
    new_password = data.get("new_password") or ""

    u = user_model.get_user_by_id(g.user_id)
    if not u or not user_model.verify_password(u, old_password):
        return jsonify({"error": "Current password is incorrect"}), 401
    if not is_valid_password(new_password):
        return jsonify({"error": "New password must be at least 8 characters and include letters and numbers"}), 400

    user_model.update_password(g.user_id, new_password)
    return jsonify({"message": "Password updated"})
