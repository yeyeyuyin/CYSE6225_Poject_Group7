from flask import Blueprint, request, jsonify

from models import video as video_model

search_bp = Blueprint("search", __name__)


@search_bp.get("")
def search_videos():
    """Real-time keyword search with simple fuzzy (substring) matching against
    title and description. Fine for a class-project catalog size; swap for
    OpenSearch/Algolia if the dataset grows."""
    q = (request.args.get("q") or "").strip().lower()
    if not q:
        return jsonify([])

    videos = [video_model.with_avg_rating(v) for v in video_model.list_videos()]
    matches = [
        v
        for v in videos
        if q in v.get("title", "").lower() or q in v.get("description", "").lower()
    ]
    return jsonify(matches)
