######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

from flask import jsonify, request, abort, url_for
from service.models import Product
from service.common import status  # HTTP Status Codes
from . import app

def check_content_type(content_type):
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              f"Content-Type must be {content_type}")
    if request.headers["Content-Type"] != content_type:
        app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              f"Content-Type must be {content_type}")

@app.route("/health")
def healthcheck():
    return jsonify(status=200, message="OK"), status.HTTP_200_OK

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/products", methods=["POST"])
def create_products():
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)
    message = {"message": "Success", "product": product.serialize()}
    location_url = url_for("get_products", product_id=product.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

@app.route("/products", methods=["GET"])
def list_products():
    app.logger.info("Request to list all products")
    category = request.args.get("category")
    available = request.args.get("available")
    products = Product.all()
    if category:
        products = [p for p in products if p.category.name.lower() == category.lower()]
    if available:
        available_bool = available.lower() in ["true", "1", "yes"]
        products = [p for p in products if p.available == available_bool]
    results = [p.serialize() for p in products]
    return jsonify({"message": "Success", "results": results}), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    app.logger.info("Request to Retrieve a product with id [%s]", product_id)
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND,
              f"Product with id '{product_id}' was not found.")
    app.logger.info("Returning product: %s", product.name)
    return jsonify({"message": "Success", "product": product.serialize()}), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND,
              f"Product with id '{product_id}' was not found.")
    data = request.get_json()
    product.deserialize(data)
    product.update()
    return jsonify({"message": "Success", "product": product.serialize()}), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    app.logger.info("Request to Delete a product with id [%s]", product_id)
    product = Product.find(product_id)
    if product:
        product.delete()
    return jsonify({"message": "Product has been Deleted!"}), status.HTTP_200_OK
