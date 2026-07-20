"""History table.
PK: user_id (S)   SK: sort_key (S) = "<iso-timestamp>#<video_id>"
Sort key embeds the timestamp so a query naturally returns items in time order.
"""
import datetime

from config import Config
from extensions import dynamodb

table = dynamodb.Table(Config.TABLE_HISTORY)


def log_view(user_id: str, video_id: str):
    timestamp = datetime.datetime.utcnow().isoformat()
    table.put_item(
        Item={
            "user_id": user_id,
            "sort_key": f"{timestamp}#{video_id}",
            "video_id": video_id,
            "viewed_at": timestamp,
        }
    )


def list_history(user_id: str, limit: int = 50):
    resp = table.query(
        KeyConditionExpression="user_id = :u",
        ExpressionAttributeValues={":u": user_id},
        ScanIndexForward=False,  # most recent first, since sort_key starts with timestamp
        Limit=limit,
    )
    return resp.get("Items", [])
