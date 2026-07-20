"""Ratings table.
PK: video_id (S)   SK: user_id (S)
One item per (video, user) pair -- lets a user update their existing rating.
"""
import datetime

from config import Config
from extensions import dynamodb

table = dynamodb.Table(Config.TABLE_RATINGS)


def get_rating(video_id: str, user_id: str):
    resp = table.get_item(Key={"video_id": video_id, "user_id": user_id})
    return resp.get("Item")


def put_rating(video_id: str, user_id: str, score: int):
    table.put_item(
        Item={
            "video_id": video_id,
            "user_id": user_id,
            "score": score,
            "updated_at": datetime.datetime.utcnow().isoformat(),
        }
    )
