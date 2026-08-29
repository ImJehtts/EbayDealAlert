"""
Local script to test eBay API script
Fetches OAuth token and searches buy now listings under the desired price point
"""

import os
import time
import requests
from dotenv import load_dotenv

#reads .env into enviroment variables 
load_dotenv()

CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

#URLs that API calls to for sending requests (1. For the OAuth token and 2. For finding items)
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

MARKETPLACE_ID = "EBAY_CA"

#Token cache to help when moving to lamda 
_cached_token = None
_token_expires_at = 0

def get_token():
    #This function will return eBay OAuth token, reusing the cached one if it exists 
    global _cached_token, _token_expires_at

    #If current cached token has more than 5 minutes left
    if _cached_token and time.time() < _token_expires_at - 300:
        return _cached_token

    #If either are missing or typed wrong from .env, raise error 
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError(
            "Missing credentials. Check that .env exists and uses "
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


def search_listings(keyword, max_price, currency="CAD", limit=10):
    #This function returns Buy Now listing matching keyword and max_price or below
    token = get_token()

    #filters being passed into Ebay API 
    filter_string = (
        f"buyingOptions:{{FIXED_PRICE}}"
        f"price:[..{max_price}],",
        f"priceCurrency:{currency}"
    )

    #Requesting buy now items from Ebay API
    response = requests.get(
        SEARCH_URL,
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": MARKETPLACE_ID,
        },
        params={"q": keyword, filter: filter_string, "limit": limit},
        timeout=10,
    )

    #raises an exception for any 4xx/5xx
    response.raise_for_status()    


    return [_parse_item(item) for item in response.json().get("itemSummaries", [])]

def _parse_item(item):
    #Return only the listing attributes needed from Ebay API

    #Try to get primary image first, if not found, .get() on empty dict gets None which
    #causes the or block to run
    image_url = (
        item.get("image", {}).get("imageURL")
        or (item.get("thumbnailImages") or [{}])[0].get("imageUrl")
    )

    return {
        "itemId": item.get("itemId"),
        "title": item.get("title"),
        "price": float(item.get("price", {}).get("value", 0)),
        "currency": item.get("price", {}).get("currency"),
        "itemWebUrl": item.get("itemWebUrl"),
        "imageUrl": image_url,
        "isVariationGroup": "itemGroupHref" in item,
    }