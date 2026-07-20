"""Basic smoke test. Run with: pytest backend/tests
Note: requires DynamoDB tables to exist (or DYNAMODB_ENDPOINT_URL pointed at
a local DynamoDB) since app.py wires up boto3 resources at import time."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app


def test_health_check():
    app = create_app()
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
