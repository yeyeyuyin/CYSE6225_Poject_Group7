from flask import Blueprint, request, jsonify, g

from models import video as video_model
from models import rating as rating_model
from utils.auth_helpers import require_auth
from utils.validators import is_valid_rating

ratings_bp = Blueprint("ratings", __name__)


@ratings_bp.post("/<video_id>/rating")
@require_auth
def submit_rating(video_id):
    if not video_model.get_video(video_id):
        return jsonify({"error": "Video not found"}), 404

    data = request.get_json(silent=True) or {}
    score = data.get("score")
    if not is_valid_rating(score):
        return jsonify({"error": "score must be an integer between 0 and 5"}), 400
    score = int(score)

    existing = rating_model.get_rating(video_id, g.user_id)
    rating_model.put_rating(video_id, g.user_id, score)

    if existing:
        sum_delta = score - int(existing["score"])
        count_delta = 0
    else:
        sum_delta = score
        count_delta = 1

    rating_sum, rating_count = video_model.apply_rating_delta(video_id, sum_delta, count_delta)
    avg = round(rating_sum / rating_count, 2) if rating_count else 0
    return jsonify({"avg_rating": avg, "rating_count": rating_count, "your_score": score})
