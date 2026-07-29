"""Seeds sample users and videos into DynamoDB from the JSON files in seeds/.

Run AFTER create_tables.py, from the backend/ dir with the venv active:

    python3 scripts/seed_data.py

Idempotent: re-running skips users/videos that already exist, so it's safe to
run repeatedly. Test fixtures live in backend/seeds/*.json (version-controlled)
so the team can edit them without touching code.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import Config
from models import user as user_model
from models import video as video_model

SEEDS_DIR = os.path.join(os.path.dirname(__file__), "..", "seeds")


def load_seed(filename):
    with open(os.path.join(SEEDS_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


def seed_users():
    for u in load_seed("users.json"):
        if user_model.get_user_by_email(u["email"]):
            print(f"[skip]   user {u['email']} already exists")
            continue
        created = user_model.create_user(u["email"], u["password"], u.get("nickname", ""), u.get("role", "user"))
        # NOTE: create_user hashes the password, so these accounts can actually log in.
        print(f"[create] user {created['email']} ({created['user_id']})")


def seed_videos():
    existing_titles = {v.get("title") for v in video_model.list_videos()}
    for v in load_seed("videos.json"):
        if v["title"] in existing_titles:
            print(f"[skip]   video {v['title']!r} already exists")
            continue
        created = video_model.create_video(
            title=v["title"],
            description=v.get("description", ""),
            tags=v.get("tags", []),
            sources=v.get("sources", []),
            thumbnail_url=v.get("thumbnail_url", ""),
        )
        print(f"[create] video {created['title']!r} ({created['video_id']})")


def main():
    print(f"Seeding into table prefix {Config.TABLE_PREFIX!r} "
          f"(endpoint: {Config.DYNAMODB_ENDPOINT_URL or 'real AWS'})\n")
    seed_users()
    seed_videos()
    print("\nDone.")


if __name__ == "__main__":
    main()
