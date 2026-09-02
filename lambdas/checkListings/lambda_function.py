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

#seconds * minutes * hours * days
TTL_SECONDS = 60 * 60 * 24 * 30

def lambda_handler(event, context):
    #Scan reads the whole table. This is fine for now at my current scale but could fix later
    
    #scan() reads the entire table and gives back every row
    response = alerts_table.scan()
    #response["Items"] pulls out the list that matters from response
    alerts = [a for a in response["Items"] if a.get("active")]

    print(f"Scanning {len(alerts)} active alerts")
    new_matches = 0

    #Scan eBay API to find listings that match the value for each alert in alerts table
    for alert in alerts:
        listings = search_listings(
            alert["keyword"],
            alert["maxPrice"],
            currency=alert.get("currency", "CAD"),
            category_id=alert.get("categoryId"),
        )

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

            new_matches += 1

            #Can update later when Email time for whole Title
            print(f"  ${listing['price']} — {listing['title'][:50]}")
            print(f"      {listing['itemWebUrl']}")

    print(f"{new_matches} new matches")
    return {"scanned": len(alerts)}