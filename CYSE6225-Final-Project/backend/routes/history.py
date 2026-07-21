from flask import Blueprint, jsonify, g

from models import history as history_model
from models import video as video_model
from utils.auth_helpers import require_auth

history_bp = Blueprint("history", __name__)


@history_bp.get("")
@require_auth
def list_history():
    entries = history_model.list_history(g.user_id)
    result = []
    seen = set()  # entries are newest-first; keep only the most recent view per video
    for entry in entries:
        video_id = entry["video_id"]
        if video_id in seen:
            continue
        seen.add(video_id)
        v = video_model.get_video(video_id)
        if v:
            item = video_model.with_avg_rating(v)
            item["viewed_at"] = entry["viewed_at"]
            result.append(item)
    return jsonify(result)
