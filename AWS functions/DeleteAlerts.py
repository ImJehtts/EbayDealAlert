import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Alerts")


def lambda_handler(event, context):
    path = event.get("pathParameters") or {}
    params = event.get("queryStringParameters") or {}

    alert_id = path.get("alertId")
    email = params.get("email")

    if not alert_id or not email:
        return _response(400, {"error": "alertId (path) and email (query) are both required"})

    table.delete_item(
        Key={
            "userId": email,
            "alertId": alert_id,
        }
    )

    return _response(200, {"deleted": alert_id})


def _response(status, payload):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }

