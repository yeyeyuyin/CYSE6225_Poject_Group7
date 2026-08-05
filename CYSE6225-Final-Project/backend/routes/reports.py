from flask import Blueprint, request, jsonify, g

from models import video as video_model
from models import report as report_model
from utils.auth_helpers import require_auth

reports_bp = Blueprint("reports", __name__)


@reports_bp.post("/<video_id>/report")
@require_auth
def report_broken_link(video_id):
    if not video_model.get_video(video_id):
        return jsonify({"error": "Video not found"}), 404

    data = request.get_json(silent=True) or {}
    source_name = data.get("source_name", "")
    note = data.get("note", "")

    report = report_model.create_report(video_id, g.user_id, source_name, note)
    return jsonify({"message": "Thanks for reporting — we'll take a look!", "report_id": report["report_id"]}), 201
