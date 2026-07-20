"""Favorites table.
PK: user_id (S)   SK: video_id (S)
"""
import datetime

from config import Config
from extensions import dynamodb

table = dynamodb.Table(Config.TABLE_FAVORITES)


def add_favorite(user_id: str, video_id: str):
    table.put_item(
        Item={
            "user_id": user_id,
            "video_id": video_id,
            "created_at": datetime.datetime.utcnow().isoformat(),
        }
    )


def remove_favorite(user_id: str, video_id: str):
    table.delete_item(Key={"user_id": user_id, "video_id": video_id})


def is_favorite(user_id: str, video_id: str) -> bool:
    resp = table.get_item(Key={"user_id": user_id, "video_id": video_id})
    return "Item" in resp


def list_favorites(user_id: str):
    resp = table.query(
        KeyConditionExpression="user_id = :u",
        ExpressionAttributeValues={":u": user_id},
    )
    return resp.get("Items", [])
