"""
checkListings: scheduled scan of every active alert.
"""

import boto3

dynamodb = boto3.resource("dynamodb")
alerts_table = dynamodb.Table("Alerts")


def lambda_handler(event, context):
    #Scan reads the whole table. This is fine for now at my current scale but could fix later
    response = alerts_table.scan()
    alerts = [a for a in response["Items"] if a.get("active")]

    print(f"Found {len(alerts)} alerts")
    for alert in alerts:
        print(alert)

    return {"scanned": len(alerts)}