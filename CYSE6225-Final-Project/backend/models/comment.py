"""Comments table.
PK: video_id (S)   SK: comment_id (S)
"""
import datetime

from config import Config
from extensions import dynamodb
from utils.ids import new_id

table = dynamodb.Table(Config.TABLE_COMMENTS)


def add_comment(video_id: str, user_id: str, nickname: str, text: str):
    comment_id = new_id()
    item = {
        "video_id": video_id,
        "comment_id": comment_id,
        "user_id": user_id,
        "nickname": nickname,
        "text": text,
        "likes": 0,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    table.put_item(Item=item)
    return item


def list_comments(video_id: str):
    resp = table.query(
        KeyConditionExpression="video_id = :v",
        ExpressionAttributeValues={":v": video_id},
        ScanIndexForward=False,  # newest first (comment_id isn't time-ordered,
        # so the route layer re-sorts by created_at -- see routes/comments.py)
    )
    return resp.get("Items", [])


def like_comment(video_id: str, comment_id: str):
    resp = table.update_item(
        Key={"video_id": video_id, "comment_id": comment_id},
        UpdateExpression="SET likes = if_not_exists(likes, :zero) + :one",
        ExpressionAttributeValues={":zero": 0, ":one": 1},
        ReturnValues="UPDATED_NEW",
    )
    return int(resp["Attributes"]["likes"])
