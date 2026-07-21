from flask import Blueprint, request, jsonify, g

from models import favorite as favorite_model
from models import video as video_model
from utils.auth_helpers import require_auth

favorites_bp = Blueprint("favorites", __name__)


@favorites_bp.get("")
@require_auth
def list_favorites():
    favs = favorite_model.list_favorites(g.user_id)
    videos = []
    for f in favs:
        v = video_model.get_video(f["video_id"])  # fetch once per favorite
        if v:
            videos.append(video_model.with_avg_rating(v))
    return jsonify(videos)


@favorites_bp.post("/<video_id>")
@require_auth
def add_favorite(video_id):
    if not video_model.get_video(video_id):
        return jsonify({"error": "Video not found"}), 404
    favorite_model.add_favorite(g.user_id, video_id)
    return jsonify({"message": "Added to watchlist"}), 201


@favorites_bp.delete("/<video_id>")
@require_auth
def remove_favorite(video_id):
    favorite_model.remove_favorite(g.user_id, video_id)
    return jsonify({"message": "Removed from watchlist"})
