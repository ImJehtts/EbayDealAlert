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

#URLs that API calls with send requests to (1. For the OAuth token and 2. For finding items)
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

    #Same request as postman. Requesting for a fresh OAuth token
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