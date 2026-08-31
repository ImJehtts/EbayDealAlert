import json
import uuid
import boto3
from decimal import Decimal
from datetime import datetime, timezone


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Alerts")

def lambda_handler(event, context):

    try:
        body = json.loads(event["body"])
    except (TypeError, KeyError):
        return _response(400, {"error": "Invalid JSON body"})

    for field in ["email", "keyword", "maxPrice"]:
            if not body.get(field):
                return _response(400, {"error": f"Missing required field: {field}"})
    
    alert_id = str(uuid.uuid4())

    item = {
        "userId": body["email"],
        "alertId": alert_id,
        "email": body["email"],
        "keyword": body["keyword"],
        "maxPrice": Decimal(str(body["maxPrice"])),
        "currency": body.get("currency", "CAD"),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "active": True,
    }

    if body.get("categoryId"):
        item["categoryId"] = body["categoryId"]
        item["categoryName"] = body.get("categoryName", "")

    table.put_item(Item=item)
    return _response(201, {"alertId": alert_id})

def _response(status, payload):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }