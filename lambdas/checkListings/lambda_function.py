"""
checkListings: scheduled scan of every active alert.
"""
#Reminder about token: checkListings calls search_listings(), which calls get_token()

import boto3
import time
from search import search_listings

dynamodb = boto3.resource("dynamodb")
alerts_table = dynamodb.Table("Alerts")
notified_table = dynamodb.Table("NotifiedItems")
ses = boto3.client("ses")

SENDER = "eBay Deal Finder <ebaydealfinderaws@gmail.com>"

#seconds * minutes * hours * days
TTL_SECONDS = 60 * 60 * 24 * 30

def lambda_handler(event, context):

    #Scan reads the whole table. This is fine for now at my current scale but could fix later
    #scan() reads the entire table and gives back every row
    response = alerts_table.scan()
    #response["Items"] pulls out the list that matters from response
    alerts = [a for a in response["Items"] if a.get("active")]

    print(f"Scanning {len(alerts)} active alerts")

    #Scan eBay API to find listings that match the value for each alert in alerts table
    for alert in alerts:
        listings = search_listings(
            alert["keyword"],
            alert["maxPrice"],
            currency=alert.get("currency", "CAD"),
            category_id=alert.get("categoryId"),
        )

        #This is so every new alert can be sent in one email
        matches = []

        for listing in listings:
            dedup_key = f"{alert['alertId']}#{listing['itemId']}"

            #Grab the dict for alert Item if in NotifiedItems
            seen = notified_table.get_item(Key={"alertItemKey": dedup_key})

            #If it's in NotifiedItems cause already alerted, skip it 
            if "Item" in seen:
                continue

            notified_table.put_item(Item={
                "alertItemKey": dedup_key,
                "ttl": int(time.time() + TTL_SECONDS),
            })

            matches.append(listing)

        #If there are any new listings found, send an email with them
        if matches:
            _send_email(alert, matches)

    return {"scanned": len(alerts)}


def _send_email(alert, matches):
    """One message per alert per run, listing every new match."""

    count = len(matches)
    subject = f"{count} New {'match' if count == 1 else 'matches'} for '{alert['keyword']}'"
    lines = [f"New listings under ${alert['maxPrice']} {alert.get('currency', 'CAD')}:", ""]

    for listing in matches:
        lines.append(f"{listing['title']}")
        lines.append(f"  ${listing['price']:.2f} {listing['currency']}")
        lines.append(f"  {listing['itemWebUrl']}")
        lines.append("")

    lines.append("- eBayDealFinder")

    ses.send_email(
        Source=SENDER,
        Destination={"ToAddresses": [alert["email"]]},
        Message={
            "Subject": {"Data": subject},
            #Plain text but I can make it HTML later if I want
            "Body": {"Text": {"Data": "\n".join(lines)}},
        },
    )

    print(f"Emailed {alert['email']}: {count} matches for '{alert['keyword']}'")