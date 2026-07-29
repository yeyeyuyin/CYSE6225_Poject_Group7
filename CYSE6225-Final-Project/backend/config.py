import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    PORT = int(os.getenv("PORT", "5001"))  # 5000 is taken by macOS AirPlay Receiver; api.js matches this
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    TABLE_PREFIX = os.getenv("TABLE_PREFIX", "dev_")
    DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL")  # None -> real AWS

    JWT_SECRET = os.getenv("JWT_SECRET", "insecure-dev-secret-change-me")
    JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "24"))

    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]

    # DynamoDB table names (prefixed so dev/staging/prod can coexist)
    TABLE_USERS = f"{TABLE_PREFIX}Users"
    TABLE_VIDEOS = f"{TABLE_PREFIX}Videos"
    TABLE_RATINGS = f"{TABLE_PREFIX}Ratings"
    TABLE_COMMENTS = f"{TABLE_PREFIX}Comments"
    TABLE_FAVORITES = f"{TABLE_PREFIX}Favorites"
    TABLE_HISTORY = f"{TABLE_PREFIX}History"
    TABLE_REPORTS = f"{TABLE_PREFIX}Reports"

    # Avatar uploads: local disk for dev (see utils/avatar_storage.py); swap
    # that module's save_avatar() for an S3 upload when deploying, callers
    # only ever see a URL string and don't care where it's stored.
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "avatars")
    MAX_AVATAR_BYTES = 2 * 1024 * 1024  # 2MB
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # Flask-level cap, rejects oversized requests with 413
