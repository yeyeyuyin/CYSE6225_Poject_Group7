import os
from dotenv import load_dotenv

load_dotenv()


class Config:
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
