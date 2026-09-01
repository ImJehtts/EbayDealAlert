"""
Local script to test eBay API script
Fetches OAuth token and searches buy now listings under the desired price point
"""

import time
import requests
import boto3

#One client, created at import
_ssm = boto3.client("ssm", region_name="us-east-1")

def _get_parameter(name, decrypt=False):
    #Read one value out of SSM Parameter Store
    response = _ssm.get_parameter(Name=name, WithDecryption=decrypt)
    return response["Parameter"]["Value"]

#Fetched at import, not inside get_token(). On Lambda this runs once per cold
#   start instead of once per invocation
CLIENT_ID = _get_parameter("/ebay-deal-finder/client-id")
CLIENT_SECRET = _get_parameter("/ebay-deal-finder/client-secret", decrypt=True)

#URLs that API calls to for sending requests (1. For the OAuth token and 2. For finding items)
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

MARKETPLACE_ID = "EBAY_CA"

#Token cache to help when moving to lamda 
_cached_token = None
_token_expires_at = 0


def get_token():
    """
    This function will return eBay OAuth token, reusing the cached one if it exists 
    """

    global _cached_token, _token_expires_at

    #If current cached token has more than 5 minutes left
    if _cached_token and time.time() < _token_expires_at - 300:
        return _cached_token

    #If either are missing or typed wrong, raise error 
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError(
            "Missing credentials. Check that credentials exists and uses "
            "EBAY_CLIENT_ID / EBAY_CLIENT_SECRET."
        )

    #Requesting for a fresh OAuth token
    response = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),  
        headers = {"Content-Type": "application/x-www-form-urlencoded"},
        data= {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        },
        timeout=10,
    )

    #raises an exception for any 4xx/5xx
    response.raise_for_status()    

    payload = response.json()
    _cached_token = payload["access_token"]
    _token_expires_at = time.time() + payload["expires_in"]
    return _cached_token


def search_listings(keyword, max_price, currency="CAD", limit=10, category_id=None):
    """This function returns Buy Now listing matching keyword and max_price or below"""
    token = get_token()

    #filters being passed into Ebay API 
    filter_string = (
        f"buyingOptions:{{FIXED_PRICE}}"
        f"price:[..{max_price}],",
        f"priceCurrency:{currency}"
    )

    #Requesting buy now items from Ebay API
    params = {"q": keyword, "filter": filter_string, "limit": limit}
    if category_id:
        params["category_ids"] = category_id

    response = requests.get(
        SEARCH_URL,
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": MARKETPLACE_ID,
        },
        params= params,
        timeout=10,
    )


    #raises an exception for any 4xx/5xx
    response.raise_for_status()    


    return [_parse_item(item) for item in response.json().get("itemSummaries", [])]


def _parse_item(item):
    """
    Return only the listing attributes needed from Ebay API
    """

    #Try to get primary image first, if not found, .get() on empty dict gets None which
    #causes the or block to run
    image_url = (
        item.get("image", {}).get("imageUrl")
        or (item.get("thumbnailImages") or [{}])[0].get("imageUrl")
    )

    return {
        "itemId": item.get("itemId"),
        "title": item.get("title"),
        "price": float(item.get("price", {}).get("value", 0)),
        "currency": item.get("price", {}).get("currency"),
        "itemWebUrl": item.get("itemWebUrl"),
        "imageUrl": image_url,
        # A "variation group" is one listing covering several options (sizes, colours), each with its own price
        # eBay reports one of them, not the cheapest, so a flagged listing's price may not be what you'd pay when you open the listing.
        "isVariationGroup": "itemGroupHref" in item,
    }


def get_category_refinements(keyword, limit=1):
    #NEED TO ADD COMMENTS#
    token = get_token()

    params = {"q": keyword, "fieldgroups": "CATEGORY_REFINEMENTS", "limit": limit}

    response = requests.get(
        SEARCH_URL,
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": MARKETPLACE_ID,
        },
        params= params,
        timeout=10,
    )
    response.raise_for_status()    

    distributions = response.json().get("refinement", {}).get("categoryDistributions", [])

    categories = [
        {
            "categoryId": category.get("categoryId"),
            "categoryName": category.get("categoryName"),
            # eBay sends matchCount as a string here, same trap as price.value.
            "matchCount": int(category.get("matchCount", 0)),
        }
        for category in distributions
    ]

    return sorted(categories, key=lambda category: category["matchCount"], reverse=True)[:15]


if __name__ == "__main__":
    KEYWORD = "iphone 17"
    MAX_PRICE = 800

    print(f"Searching: '{KEYWORD}' under ${MAX_PRICE} CAD\n")
    print("\nCategories:")
    for category in get_category_refinements(KEYWORD):
        print(f"  {category['matchCount']:>6}  {category['categoryName']}  ({category['categoryId']})")

    listings = search_listings(KEYWORD, MAX_PRICE)

    if not listings:
        print("No listings find. Try different searches or try again later")

    for n, listing in enumerate(listings, start=1):
        # Tag multi-variation listings so the price is read with suspicion and I can add to in future if needed.
        flag = "  [variation group]" if listing["isVariationGroup"] else ""
        print(f"{n}. {listing['title'][:70]}{flag}")
        print(f"   ${listing['price']:.2f} {listing['currency']}")
        print(f"   {listing['itemWebUrl'][:90]}")
        print(f"   img: {'yes' if listing['imageUrl'] else 'MISSING'}\n")

    print(f"{len(listings)} listing(s) found")