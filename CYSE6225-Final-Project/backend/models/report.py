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
