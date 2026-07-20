"""Shared AWS resource clients, initialized once and imported everywhere else."""
import boto3
from config import Config

_kwargs = {"region_name": Config.AWS_REGION}
if Config.DYNAMODB_ENDPOINT_URL:
    _kwargs["endpoint_url"] = Config.DYNAMODB_ENDPOINT_URL

dynamodb = boto3.resource("dynamodb", **_kwargs)
