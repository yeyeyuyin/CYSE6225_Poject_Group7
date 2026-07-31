"""Creates all DynamoDB tables the backend needs.

Usage:
    python3 create_tables.py --region us-east-1 --prefix dev_
    python3 create_tables.py --endpoint http://localhost:8000   # local DynamoDB

Tables are on-demand (PAY_PER_REQUEST): no capacity to provision or tune, and
idle tables cost nothing beyond the storage of the data already in them --
important for an environment that gets torn down and rebuilt between test
sessions.

Safe to re-run: skips any table that already exists.
"""
import argparse
import sys

import boto3
from botocore.exceptions import ClientError


def table_spec(prefix: str):
    return [
        {
            "TableName": f"{prefix}Users",
            "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
            "AttributeDefinitions": [
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "email-index",
                    "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        },
        {
            "TableName": f"{prefix}Videos",
            "KeySchema": [{"AttributeName": "video_id", "KeyType": "HASH"}],
            "AttributeDefinitions": [{"AttributeName": "video_id", "AttributeType": "S"}],
        },
        {
            "TableName": f"{prefix}Ratings",
            "KeySchema": [
                {"AttributeName": "video_id", "KeyType": "HASH"},
                {"AttributeName": "user_id", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "video_id", "AttributeType": "S"},
                {"AttributeName": "user_id", "AttributeType": "S"},
            ],
        },
        {
            "TableName": f"{prefix}Comments",
            "KeySchema": [
                {"AttributeName": "video_id", "KeyType": "HASH"},
                {"AttributeName": "comment_id", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "video_id", "AttributeType": "S"},
                {"AttributeName": "comment_id", "AttributeType": "S"},
            ],
        },
        {
            "TableName": f"{prefix}Favorites",
            "KeySchema": [
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "video_id", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "video_id", "AttributeType": "S"},
            ],
        },
        {
            "TableName": f"{prefix}History",
            "KeySchema": [
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "sort_key", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "sort_key", "AttributeType": "S"},
            ],
        },
        {
            "TableName": f"{prefix}Reports",
            "KeySchema": [{"AttributeName": "report_id", "KeyType": "HASH"}],
            "AttributeDefinitions": [{"AttributeName": "report_id", "AttributeType": "S"}],
        },
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--prefix", default="dev_", help="Must match TABLE_PREFIX in backend/.env")
    parser.add_argument("--endpoint", default=None, help="Optional: local DynamoDB endpoint, e.g. http://localhost:8000")
    args = parser.parse_args()

    kwargs = {"region_name": args.region}
    if args.endpoint:
        kwargs["endpoint_url"] = args.endpoint

    client = boto3.client("dynamodb", **kwargs)
    existing = set(client.list_tables()["TableNames"])

    for spec in table_spec(args.prefix):
        name = spec["TableName"]
        if name in existing:
            print(f"[skip] {name} already exists")
            continue
        try:
            client.create_table(BillingMode="PAY_PER_REQUEST", **spec)
            print(f"[create] {name} ...")
        except ClientError as e:
            print(f"[error] {name}: {e}", file=sys.stderr)

    print("\nWaiting for tables to become ACTIVE (this can take ~30-60s on real AWS)...")
    waiter = client.get_waiter("table_exists")
    for spec in table_spec(args.prefix):
        waiter.wait(TableName=spec["TableName"])
    print("All tables ready.")


if __name__ == "__main__":
    main()
