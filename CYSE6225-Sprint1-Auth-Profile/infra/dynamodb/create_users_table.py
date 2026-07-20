"""Creates only the Users table -- everything Sprint 1 needs.
(The full project's infra/dynamodb/create_tables.py creates all 7 tables;
use this smaller script while only Auth/Profile exist.)

Usage:
    python3 create_users_table.py --region us-east-1 --prefix dev_
    python3 create_users_table.py --endpoint http://localhost:8000   # local DynamoDB
"""
import argparse
import sys

import boto3
from botocore.exceptions import ClientError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--prefix", default="dev_", help="Must match TABLE_PREFIX in backend/.env")
    parser.add_argument("--endpoint", default=None)
    args = parser.parse_args()

    kwargs = {"region_name": args.region}
    if args.endpoint:
        kwargs["endpoint_url"] = args.endpoint

    client = boto3.client("dynamodb", **kwargs)
    table_name = f"{args.prefix}Users"

    if table_name in client.list_tables()["TableNames"]:
        print(f"[skip] {table_name} already exists")
        return

    try:
        client.create_table(
            TableName=table_name,
            BillingMode="PROVISIONED",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "email-index",
                    "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                }
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        print(f"[create] {table_name} ...")
    except ClientError as e:
        print(f"[error] {table_name}: {e}", file=sys.stderr)
        sys.exit(1)

    client.get_waiter("table_exists").wait(TableName=table_name)
    print("Users table ready.")


if __name__ == "__main__":
    main()
