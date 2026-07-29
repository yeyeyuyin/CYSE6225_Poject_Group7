from flask import Blueprint, request, jsonify, g

from models import video as video_model
from models import report as report_model
from models import user as user_model
from utils.auth_helpers import require_auth, require_admin

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


@reports_bp.get("/reports")
@require_admin
def list_reports():
    """Admin dashboard feed: every report, enriched with the video title and
    reporter email so the table doesn't need N follow-up requests."""
    reports = report_model.list_reports()
    reports.sort(key=lambda r: r["created_at"], reverse=True)

    for r in reports:
        video = video_model.get_video(r["video_id"])
        r["video_title"] = video["title"] if video else None
        reporter = user_model.get_user_by_id(r["user_id"])
        r["reporter_email"] = reporter["email"] if reporter else None

    return jsonify(reports)


@reports_bp.put("/reports/<report_id>")
@require_admin
def update_report(report_id):
    if not report_model.get_report(report_id):
        return jsonify({"error": "Report not found"}), 404

    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("open", "reviewed", "resolved"):
        return jsonify({"error": "status must be one of: open, reviewed, resolved"}), 400

    updated = report_model.update_report_status(report_id, status)
    return jsonify(updated)


@reports_bp.delete("/reports/<report_id>")
@require_admin
def delete_report(report_id):
    if not report_model.get_report(report_id):
        return jsonify({"error": "Report not found"}), 404
    report_model.delete_report(report_id)
    return jsonify({"message": "Report deleted"})
