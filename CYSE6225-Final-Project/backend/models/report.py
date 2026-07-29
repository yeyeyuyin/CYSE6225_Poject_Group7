"""Reports table (broken link reports).
PK: report_id (S)
"""
import datetime

from config import Config
from extensions import dynamodb
from utils.ids import new_id

table = dynamodb.Table(Config.TABLE_REPORTS)


def create_report(video_id: str, user_id: str, source_name: str = "", note: str = ""):
    report_id = new_id()
    item = {
        "report_id": report_id,
        "video_id": video_id,
        "user_id": user_id,
        "source_name": source_name,
        "note": note,
        "status": "open",  # open -> reviewed -> resolved
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    table.put_item(Item=item)
    return item


def get_report(report_id: str):
    resp = table.get_item(Key={"report_id": report_id})
    return resp.get("Item")


def list_reports():
    """Full scan — fine at class-project scale (see video_model.list_videos)."""
    items = []
    resp = table.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))
    return items


def update_report_status(report_id: str, status: str):
    table.update_item(
        Key={"report_id": report_id},
        UpdateExpression="SET #s = :status",  # "status" is a DynamoDB reserved word
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":status": status},
    )
    return get_report(report_id)


def delete_report(report_id: str):
    table.delete_item(Key={"report_id": report_id})
