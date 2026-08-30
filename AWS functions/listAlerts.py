import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Alerts")

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    email = params.get('email')

    if not email:
        return _response(400, {"error": "email query parameter is required"})

    result = table.query(
        KeyConditionExpression=Key("userId").eq(email)
    )

    return _response(200, {"alerts": result["Items"]})


def _decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Not JSON serializable: {type(obj)}")


def _response(status, payload):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload, default=_decimal_default),
    }
