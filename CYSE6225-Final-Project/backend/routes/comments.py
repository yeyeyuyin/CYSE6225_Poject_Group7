from flask import Blueprint, request, jsonify, g

from models import video as video_model
from models import comment as comment_model
from models import user as user_model
from utils.auth_helpers import require_auth, optional_auth

comments_bp = Blueprint("comments", __name__)


@comments_bp.get("/<video_id>/comments")
@optional_auth
def list_comments(video_id):
    comments = comment_model.list_comments(video_id)
    comments.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    return jsonify(comments)


@comments_bp.post("/<video_id>/comments")
@require_auth
def add_comment(video_id):
    if not video_model.get_video(video_id):
        return jsonify({"error": "Video not found"}), 404

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Comment text is required"}), 400

    u = user_model.get_user_by_id(g.user_id)
    nickname = u.get("nickname", "Anonymous") if u else "Anonymous"
    comment = comment_model.add_comment(video_id, g.user_id, nickname, text)
    return jsonify(comment), 201


@comments_bp.post("/<video_id>/comments/<comment_id>/like")
@require_auth
def like_comment(video_id, comment_id):
    new_likes = comment_model.like_comment(video_id, comment_id)
    return jsonify({"likes": new_likes})
