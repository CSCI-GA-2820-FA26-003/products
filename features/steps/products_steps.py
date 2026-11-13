"""Steps for preparing Products data through the REST API."""

import requests
from behave import given  # pylint: disable=no-name-in-module
from compare3 import expect

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
WAIT_TIMEOUT = 60


@given("the following products")
def step_impl(context):
    """Clear the product catalog and seed it with the feature table."""
    rest_endpoint = f"{context.base_url}/products"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)

    for product in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{product['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    for row in context.table:
        payload = {
            "name": row["name"],
            "description": row["description"],
            "category": row["category"],
            "price": row["price"],
            "stock": int(row["stock"]),
        }
        if "image_url" in context.table.headings:
            payload["image_url"] = row["image_url"]

        context.resp = requests.post(
            rest_endpoint, json=payload, timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
