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

from decimal import Decimal, DecimalException
from flask import jsonify, request, abort, url_for
from flask import current_app as app  # Import Flask application
from flask_restx import Namespace, Resource, fields

from service.models import Product, DataValidationError
from service.common import status  # HTTP Status Codes
from service import api

products_ns = Namespace("products", description="Product operations")
api.add_namespace(products_ns)
error_model = products_ns.model(
    "Error",
    {
        "status": fields.Integer(description="HTTP status code", example=400),
        "error": fields.String(description="HTTP error name", example="Bad Request"),
        "message": fields.String(description="Details about the error"),
    },
)
product_input = products_ns.model(
    "ProductInput",
    {
        "name": fields.String(
            required=True, description="Product name", example="Blue Shirt"
        ),
        "description": fields.String(description="Product description"),
        "category": fields.String(description="Product category"),
        "price": fields.Float(description="Product price", example=19.99),
        "stock": fields.Integer(description="Stock quantity", example=10),
        "image_url": fields.String(description="Product image URL"),
    },
)
product_model = products_ns.model(
    "Product",
    {
        "id": fields.Integer(readonly=True, description="Unique product ID"),
        "name": fields.String(description="Product name", example="Blue Shirt"),
        "description": fields.String(description="Product description"),
        "category": fields.String(description="Product category"),
        "price": fields.String(description="Product price", example="19.99"),
        "stock": fields.Integer(description="Stock quantity", example=10),
        "image_url": fields.String(description="Product image URL"),
        "created_at": fields.DateTime(readonly=True, description="Creation time"),
        "updated_at": fields.DateTime(readonly=True, description="Last update time"),
    },
)

stock_quantity_input = products_ns.model(
    "StockQuantityInput",
    {
        "quantity": fields.Integer(
            required=True,
            min=1,
            description="Number of units",
            example=3,
        ),
    },
)


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health", methods=["GET"])
def health():
    """Return the health status of the service"""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################
def delete_product(product_id):
    """Delete a Product"""
    app.logger.info("Request to delete product with id: %s", product_id)
    product = Product.find(product_id)

    if product:
        app.logger.info("Product with id [%s] found, deleting it.", product_id)
        product.delete()

    app.logger.info("Product with id [%s] delete complete.", product_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL PRODUCTS
######################################################################
def list_products():
    """Returns Products filtered by name, category, and/or price range"""
    app.logger.info("Request for product list")

    name = request.args.get("name")
    category = request.args.get("category")
    min_value, max_value = parse_price_range(
        request.args.get("min_price"), request.args.get("max_price")
    )

    query = Product.query
    if name is not None:
        app.logger.info("Filtering by name: %s", name)
        query = query.filter(Product.name == name)
    if category is not None:
        app.logger.info("Filtering by category: %s", category)
        query = query.filter(Product.category == category)
    if min_value is not None:
        query = query.filter(Product.price >= min_value)
    if max_value is not None:
        query = query.filter(Product.price <= max_value)

    results = [product.serialize() for product in query.all()]
    app.logger.info("Returning %d products", len(results))
    return results, status.HTTP_200_OK


@products_ns.route("")
class ProductCollection(Resource):
    """Operations on the product collection."""

    @products_ns.param("name", "Exact product name", _in="query")
    @products_ns.param("category", "Exact product category", _in="query")
    @products_ns.param("min_price", "Minimum price (inclusive)", _in="query")
    @products_ns.param("max_price", "Maximum price (inclusive)", _in="query")
    @products_ns.response(200, "List of matching products", [product_model])
    @products_ns.response(400, "Invalid price filter or price range", error_model)
    @products_ns.response(405, "Method not allowed", error_model)
    def get(self):
        """List products, with optional filters."""
        return list_products()

    @products_ns.expect(product_input, validate=False)
    @products_ns.response(201, "Product created", product_model)
    @products_ns.response(400, "Invalid product data", error_model)
    @products_ns.response(405, "Method not allowed", error_model)
    @products_ns.response(415, "Content-Type must be application/json", error_model)
    def post(self):
        """Create a product."""
        return create_product()


def parse_price_range(min_price, max_price):
    """Converts the price query params to Decimals and validates them"""
    min_value = None
    max_value = None
    try:
        min_value = Decimal(min_price) if min_price is not None else None
        max_value = Decimal(max_price) if max_price is not None else None
    except (DecimalException, TypeError, ValueError):
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Invalid price: min_price and max_price must be numbers",
        )

    if (min_value is not None and not min_value.is_finite()) or (
        max_value is not None and not max_value.is_finite()
    ):
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Invalid price: min_price and max_price must be finite numbers",
        )

    if min_value is not None and max_value is not None and min_value > max_value:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Invalid price range: min_price cannot be greater than max_price",
        )
    return min_value, max_value


######################################################################
# CREATE A PRODUCT
######################################################################
def create_product():
    """Create a new product"""

    if not request.is_json:
        abort(415, description="Content-Type must be application/json")

    data = request.get_json()

    if not isinstance(data, dict):
        abort(400, description="Invalid product data")

    product = Product()

    product.deserialize(data)

    product.create()
    app.logger.info("Product with id [%s] saved!", product.id)

    location = url_for("get_products", product_id=product.id, _external=True)
    return product.serialize(), status.HTTP_201_CREATED, {"Location": location}


######################################################################
# READ A PRODUCT
######################################################################
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
    return product.serialize(), status.HTTP_200_OK


@products_ns.route("/<int:product_id>", endpoint="get_products")
class ProductResource(Resource):
    """Operations on an individual product."""

    @products_ns.param("product_id", "ID of the product to retrieve", _in="path")
    @products_ns.response(200, "Product found", product_model)
    @products_ns.response(404, "Product not found", error_model)
    @products_ns.response(405, "Method not allowed", error_model)
    def get(self, product_id):
        """Retrieve a product by its ID."""
        return get_products(product_id)

    @products_ns.param("product_id", "ID of the product to update", _in="path")
    @products_ns.expect(product_input, validate=False)
    @products_ns.response(200, "Product updated", product_model)
    @products_ns.response(400, "Invalid product data", error_model)
    @products_ns.response(404, "Product not found", error_model)
    @products_ns.response(405, "Method not allowed", error_model)
    @products_ns.response(415, "Content-Type must be application/json", error_model)
    def put(self, product_id):
        """Update a product by its ID.
        Omitted optional fields are cleared.
        """
        return update_products(product_id)

    @products_ns.param("product_id", "ID of the product to delete", _in="path")
    @products_ns.response(204, "Product deleted or already absent")
    @products_ns.response(405, "Method not allowed", error_model)
    def delete(self, product_id):
        """Delete a product by its ID."""
        return app.make_response(delete_product(product_id))


######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
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
# PURCHASE A PRODUCT
######################################################################
def purchase_product(product_id):
    """
    Purchase a single Product

    This endpoint will decrement the product's stock by one
    """
    app.logger.info("Request to purchase product with id [%s]", product_id)

    # Attempt to find the Product and abort if not found
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    quantity = read_stock_quantity() if request.get_data() else 1
    try:
        product.purchase(quantity)
    except DataValidationError as error:
        abort(status.HTTP_409_CONFLICT, str(error))

    app.logger.info(
        "Product with id [%s] purchased, stock is now %s", product.id, product.stock
    )
    return product.serialize(), status.HTTP_200_OK


@products_ns.route("/<int:product_id>/purchase")
class ProductPurchase(Resource):
    """Purchase products and decrease stock."""

    @products_ns.param("product_id", "ID of the product to purchase", _in="path")
    @products_ns.doc(body=stock_quantity_input)
    @products_ns.param(
        "payload",
        "Optional JSON body. Omit it to purchase one unit.",
        _in="body",
        required=False,
    )
    @products_ns.response(200, "Product purchased", product_model)
    @products_ns.response(400, "Invalid quantity or JSON body", error_model)
    @products_ns.response(404, "Product not found", error_model)
    @products_ns.response(405, "Method not allowed", error_model)
    @products_ns.response(409, "Insufficient stock", error_model)
    @products_ns.response(
        415,
        "Content-Type must be application/json when a body is sent",
        error_model,
    )
    def put(self, product_id):
        """Purchase the requested quantity."""
        return purchase_product(product_id)


######################################################################
# RESTOCK AN EXISTING PRODUCT
######################################################################
def restock_product(product_id):
    """Increase a product's stock"""
    app.logger.info("Request to restock product with id [%s]", product_id)

    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            description=f"Product with id '{product_id}' was not found.",
        )

    quantity = read_stock_quantity()
    product.stock = (product.stock or 0) + quantity
    product.update()
    return product.serialize(), status.HTTP_200_OK


@products_ns.route("/<int:product_id>/restock")
class ProductRestock(Resource):
    """Restock an existing product."""

    @products_ns.param("product_id", "ID of the product to restock", _in="path")
    @products_ns.expect(stock_quantity_input, validate=False)
    @products_ns.response(200, "Product restocked", product_model)
    @products_ns.response(
        400,
        "Invalid quantity, invalid JSON body, or update failed",
        error_model,
    )
    @products_ns.response(404, "Product not found", error_model)
    @products_ns.response(405, "Method not allowed", error_model)
    @products_ns.response(415, "Content-Type must be application/json", error_model)
    def post(self, product_id):
        """Add the requested quantity to stock."""
        return restock_product(product_id)


def read_stock_quantity():
    """Read and validate the requested stock quantity."""
    check_content_type("application/json")
    data = request.get_json()
    if not isinstance(data, dict):
        abort(status.HTTP_400_BAD_REQUEST, description="Invalid request body")

    quantity = data.get("quantity")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        abort(
            status.HTTP_400_BAD_REQUEST,
            description="quantity must be a positive integer",
        )
    return quantity


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
