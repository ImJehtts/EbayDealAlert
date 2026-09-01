"""
checkListings: scheduled scan of every active alert.
"""
#Reminder about token: checkListings calls search_listings(), which calls get_token()

import boto3
from search import search_listings

dynamodb = boto3.resource("dynamodb")
alerts_table = dynamodb.Table("Alerts")


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

        #prints for now to make sure it's working
        print(f"{alert['keyword']}: {len(listings)} listings")
        
        for listing in listings:
            #Can update later when Email time for whole Title
            print(f"  ${listing['price']} — {listing['title'][:60]}")
            print(f"      {listing['itemWebUrl']}")

    return {"scanned": len(alerts)}