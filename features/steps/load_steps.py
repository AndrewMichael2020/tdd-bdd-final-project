import logging
import requests
from behave import given

REST_ENDPOINT = "http://localhost:8080/products"

@given('the following products')
def step_impl(context):
    """Load products from the table into the service.
    First, clear existing products, then create new ones."""
    headers = {"Content-Type": "application/json"}
    # Retrieve current products
    response = requests.get(REST_ENDPOINT, headers=headers)
    assert response.status_code == 200, f"GET products failed: {response.text}"
    data = response.json()
    # Expect response to include a "results" key
    products = data.get("results", [])
    for product in products:
        delete_url = f"{REST_ENDPOINT}/{product['id']}"
        del_response = requests.delete(delete_url, headers=headers)
        # Our DELETE now returns a JSON message with HTTP 200
        assert del_response.status_code == 200, f"DELETE failed: {del_response.text}"
    # Now add each product from the table
    for row in context.table:
        product_data = {
            "name": row["name"],
            "description": row["description"],
            "price": row["price"],
            "available": True if row["available"].lower() == "true" else False,
            "category": row["category"]
        }
        post_response = requests.post(REST_ENDPOINT, json=product_data, headers=headers)
        assert post_response.status_code == 201, f"POST failed: {post_response.text}"
