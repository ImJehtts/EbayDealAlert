"""
getCategories: returns eBay category refinements for a keyword.
"""

import json
from search import get_category_refinements


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    keyword = params.get("q")

    if not keyword:
        return _response(400, {"error": "q query parameter is required"})

    categories = get_category_refinements(keyword)

    return _response(200, {"categories": categories})


def _response(status, payload):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }