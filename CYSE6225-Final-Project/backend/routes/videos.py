from flask import Blueprint, request, jsonify, g

from models import video as video_model
from models import favorite as favorite_model
from models import history as history_model
from utils.auth_helpers import optional_auth, require_auth

videos_bp = Blueprint("videos", __name__)


@videos_bp.get("")
@optional_auth
def list_videos():
    """List all videos, with optional ?tag= filter and ?sort=clicks|rating."""
    tag = request.args.get("tag")
    sort = request.args.get("sort")  # "clicks" | "rating"

    videos = [video_model.with_avg_rating(v) for v in video_model.list_videos()]

    if tag:
        videos = [v for v in videos if tag in (v.get("tags") or [])]

    if sort == "clicks":
        videos.sort(key=lambda v: v.get("click_count", 0), reverse=True)
    elif sort == "rating":
        videos.sort(key=lambda v: v.get("avg_rating", 0), reverse=True)

    return jsonify(videos)


@videos_bp.get("/<video_id>")
@optional_auth
def get_video(video_id):
    v = video_model.get_video(video_id)
    if not v:
        return jsonify({"error": "Video not found"}), 404

    result = video_model.with_avg_rating(v)
    if g.user_id:
        result["is_favorite"] = favorite_model.is_favorite(g.user_id, video_id)
    return jsonify(result)


@videos_bp.post("")
@require_auth
def create_video():
    """Admin/seed helper for adding catalog entries. Lock this down (or move
    behind an admin role check) before shipping — it's wide open for now so
    the team can seed data while building."""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    v = video_model.create_video(
        title=title,
        description=data.get("description", ""),
        tags=data.get("tags", []),
        sources=data.get("sources", []),
        thumbnail_url=data.get("thumbnail_url", ""),
    )
    return jsonify(video_model.with_avg_rating(v)), 201


@videos_bp.post("/<video_id>/click")
@optional_auth
def register_click(video_id):
    """Called when a user hits play on an external source. Increments the
    click counter and, if logged in, appends to watch history."""
    if not video_model.get_video(video_id):
        return jsonify({"error": "Video not found"}), 404

    new_count = video_model.increment_click_count(video_id)
    if g.user_id:
        history_model.log_view(g.user_id, video_id)

    return jsonify({"click_count": new_count})
