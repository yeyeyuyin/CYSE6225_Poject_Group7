"""Videos table.
PK: video_id (S)
Attributes: title, description, tags (SS/list), sources (list of {name,url}),
            thumbnail_url, click_count (N), rating_sum (N), rating_count (N)
"""
import datetime
import re

from config import Config
from extensions import dynamodb
from utils.ids import new_id

table = dynamodb.Table(Config.TABLE_VIDEOS)

_YOUTUBE_ID_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtube\.com/embed/|youtu\.be/)([A-Za-z0-9_-]{11})"
)


def _derive_thumbnail(video: dict) -> str:
    """Fall back to YouTube's hosted thumbnail (its own first/key frame image)
    when no thumbnail_url was set manually. Other source types (e.g. Vimeo)
    aren't covered -- their thumbnails require an API call, not just a URL
    pattern -- so they keep falling through to the frontend's placeholder."""
    if video.get("thumbnail_url"):
        return video["thumbnail_url"]
    for source in video.get("sources") or []:
        match = _YOUTUBE_ID_RE.search(source.get("url", ""))
        if match:
            return f"https://img.youtube.com/vi/{match.group(1)}/hqdefault.jpg"
    return ""


def create_video(title, description, tags, sources, thumbnail_url=""):
    video_id = new_id()
    item = {
        "video_id": video_id,
        "title": title,
        "description": description,
        "tags": tags or [],
        "sources": sources or [],  # [{"name": "Source A - YouTube", "url": "..."}]
        "thumbnail_url": thumbnail_url,
        "click_count": 0,
        "rating_sum": 0,
        "rating_count": 0,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    table.put_item(Item=item)
    return item


def get_video(video_id: str):
    resp = table.get_item(Key={"video_id": video_id})
    return resp.get("Item")


def list_videos():
    """Simple full scan — fine for a class-project-sized dataset.
    Swap for a query against a GSI (e.g. by tag) if the catalog grows."""
    items = []
    resp = table.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))
    return items


def update_video(video_id: str, title=None, description=None, tags=None, sources=None, thumbnail_url=None):
    """Admin edit. Fields left as None are unchanged. Expression attribute
    names are used unconditionally (not just when needed) to sidestep
    DynamoDB's reserved-word list entirely."""
    fields = {
        "title": title,
        "description": description,
        "tags": tags,
        "sources": sources,
        "thumbnail_url": thumbnail_url,
    }
    updates, names, values = [], {}, {}
    for i, (field, value) in enumerate(fields.items()):
        if value is not None:
            placeholder = f"#f{i}"
            updates.append(f"{placeholder} = :{field}")
            names[placeholder] = field
            values[f":{field}"] = value

    if not updates:
        return get_video(video_id)

    table.update_item(
        Key={"video_id": video_id},
        UpdateExpression="SET " + ", ".join(updates),
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
    )
    return get_video(video_id)


def delete_video(video_id: str):
    table.delete_item(Key={"video_id": video_id})


def increment_click_count(video_id: str) -> int:
    resp = table.update_item(
        Key={"video_id": video_id},
        UpdateExpression="SET click_count = if_not_exists(click_count, :zero) + :one",
        ExpressionAttributeValues={":zero": 0, ":one": 1},
        ReturnValues="UPDATED_NEW",
    )
    return int(resp["Attributes"]["click_count"])


def apply_rating_delta(video_id: str, sum_delta: int, count_delta: int):
    """Adjust rating_sum/rating_count atomically (used on new rating or rating update)."""
    resp = table.update_item(
        Key={"video_id": video_id},
        UpdateExpression=(
            "SET rating_sum = if_not_exists(rating_sum, :zero) + :sd, "
            "rating_count = if_not_exists(rating_count, :zero) + :cd"
        ),
        ExpressionAttributeValues={":zero": 0, ":sd": sum_delta, ":cd": count_delta},
        ReturnValues="UPDATED_NEW",
    )
    attrs = resp["Attributes"]
    return int(attrs["rating_sum"]), int(attrs["rating_count"])


def with_avg_rating(video: dict) -> dict:
    video = dict(video)
    count = int(video.get("rating_count", 0))
    total = int(video.get("rating_sum", 0))
    video["avg_rating"] = round(total / count, 2) if count else 0
    # Normalize DynamoDB Decimals to plain ints for a clean API payload.
    video["click_count"] = int(video.get("click_count", 0))
    video["rating_sum"] = total
    video["rating_count"] = count
    video["thumbnail_url"] = _derive_thumbnail(video)
    return video
