"""Comments table.
PK: video_id (S)   SK: comment_id (S)
"""
import datetime

from botocore.exceptions import ClientError

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
    """Increment a comment's like count. Returns the new count, or None if the
    comment doesn't exist (the ConditionExpression guards against creating a
    phantom item for a bogus comment_id)."""
    try:
        resp = table.update_item(
            Key={"video_id": video_id, "comment_id": comment_id},
            UpdateExpression="SET likes = if_not_exists(likes, :zero) + :one",
            ConditionExpression="attribute_exists(comment_id)",
            ExpressionAttributeValues={":zero": 0, ":one": 1},
            ReturnValues="UPDATED_NEW",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return None
        raise
    return int(resp["Attributes"]["likes"])
