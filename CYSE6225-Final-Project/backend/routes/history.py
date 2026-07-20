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
    for entry in entries:
        v = video_model.get_video(entry["video_id"])
        if v:
            item = video_model.with_avg_rating(v)
            item["viewed_at"] = entry["viewed_at"]
            result.append(item)
    return jsonify(result)
