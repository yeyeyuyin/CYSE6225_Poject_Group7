"""Users table.
PK: user_id (S)
GSI: email-index  (PK: email)  -- used to look up a user at login time
"""
import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from extensions import dynamodb
from utils.ids import new_id

table = dynamodb.Table(Config.TABLE_USERS)


def create_user(email: str, password: str, nickname: str, role: str = "user") -> dict:
    user_id = new_id()
    item = {
        "user_id": user_id,
        "email": email.lower(),
        "password_hash": generate_password_hash(password),
        "nickname": nickname or email.split("@")[0],
        "avatar_url": "",
        "role": role,  # "user" | "admin"
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    table.put_item(Item=item, ConditionExpression="attribute_not_exists(user_id)")
    return item


def get_user_by_id(user_id: str):
    resp = table.get_item(Key={"user_id": user_id})
    return resp.get("Item")


def get_user_by_email(email: str):
    resp = table.query(
        IndexName="email-index",
        KeyConditionExpression="email = :e",
        ExpressionAttributeValues={":e": email.lower()},
        Limit=1,
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def verify_password(user: dict, password: str) -> bool:
    return check_password_hash(user["password_hash"], password)


def update_profile(user_id: str, nickname: str = None, avatar_url: str = None):
    updates, names, values = [], {}, {}
    if nickname is not None:
        updates.append("#n = :nickname")
        names["#n"] = "nickname"
        values[":nickname"] = nickname
    if avatar_url is not None:
        updates.append("avatar_url = :avatar")
        values[":avatar"] = avatar_url
    if not updates:
        return get_user_by_id(user_id)

    kwargs = {
        "Key": {"user_id": user_id},
        "UpdateExpression": "SET " + ", ".join(updates),
        "ExpressionAttributeValues": values,
    }
    if names:
        kwargs["ExpressionAttributeNames"] = names
    table.update_item(**kwargs)
    return get_user_by_id(user_id)


def update_password(user_id: str, new_password: str):
    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="SET password_hash = :ph",
        ExpressionAttributeValues={":ph": generate_password_hash(new_password)},
    )


def public_user(user: dict) -> dict:
    """Strip sensitive fields before sending a user object to the client."""
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "nickname": user.get("nickname", ""),
        "avatar_url": user.get("avatar_url", ""),
        "role": user.get("role", "user"),
    }
