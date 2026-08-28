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

#URLs that API calls with send requests to (1. For the OAuth token and second for finding items)
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

MARKETPLACE_ID = "EBAY_CA"

#Token cache to help when moving to lamda 
_cached_token = None
_token_expires_at = 0