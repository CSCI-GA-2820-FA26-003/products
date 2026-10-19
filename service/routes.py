######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Product Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Product
"""

from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from service.models import Product, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Products Service",
            version="1.0.0",
            list_url="/products",
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Delete a Product"""
    app.logger.info("Request to delete product with id: %s", product_id)
    product = Product.find(product_id)

    if not product:
        abort(404, description="Product not found")

    product.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns all of the Products"""
    app.logger.info("Request for product list")

    # Return all of the Products
    products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return results, status.HTTP_200_OK


######################################################################
# CREATE A PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_product():
    """Create a new product"""

    if not request.is_json:
        abort(415, description="Content-Type must be application/json")

    data = request.get_json()

    if not isinstance(data, dict):
        abort(400, description="Invalid product data")

    product = Product()

    try:
        product.deserialize(data)
    except DataValidationError as error:
        abort(400, description=str(error))

    product.create()
    app.logger.info("Product with id [%s] saved!", product.id)

    response = jsonify(product.serialize())
    response.headers["Location"] = f"/products/{product.id}"
    return response, status.HTTP_201_CREATED

######################################################################
# READ A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """
    Retrieve a single Product

    This endpoint will return a Product based on its id
    """
    app.logger.info("Request to Retrieve a product with id [%s]", product_id)

    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id '{product_id}' was not found.",
        )

    app.logger.info("Returning product: %s", product.name)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product

    This endpoint will update a Product based the body that is posted
    """
    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")

    # Attempt to find the Product and abort if not found
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    # Update the Product with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product.deserialize(data)

    # Save the updates to the database
    product.update()

    app.logger.info("Product with ID: %d updated.", product.id)
    return product.serialize(), status.HTTP_200_OK


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
