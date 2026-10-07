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
Test cases for Product Model
"""

# pylint: disable=duplicate-code
from datetime import datetime
from decimal import Decimal
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Product, DataValidationError, db
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  B A S E   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCaseBase(TestCase):
    """Test Cases for common setup"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
class TestProductModel(TestCaseBase):
    """Product Model CRUS Tests"""

    def test_create_a_product(self):
        """It should create a Product add it to the database, and read it from the database"""
        products = Product.all()
        self.assertEqual(products, [])

        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        found = Product.all()
        self.assertEqual(len(found), 1)
        data = Product.find(product.id)

        self.assertEqual(data.name, product.name)
        self.assertEqual(data.created_at, product.created_at)
        self.assertEqual(data.updated_at, product.updated_at)
        self.assertEqual(data.description, product.description)
        self.assertEqual(data.category, product.category)
        self.assertEqual(data.price, product.price)
        self.assertEqual(data.stock, product.stock)
        self.assertEqual(data.image_url, product.image_url)

        self.assertEqual(f"<Product {product.name} id=[{product.id}]>", repr(data))

    def test_update_a_product(self):
        """It should update a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        logging.debug(product)
        self.assertIsNotNone(product.id)

        # Change it an save it
        product.category = "vegetables"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.category, "vegetables")

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].category, "vegetables")

    def test_update_no_id(self):
        """It should not update a Product with no id"""
        product = ProductFactory()
        product.create()
        logging.debug(product)
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 Products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)

        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("created_at", data)
        self.assertEqual(datetime.fromisoformat(data["created_at"]), product.created_at)
        self.assertIn("updated_at", data)
        self.assertEqual(datetime.fromisoformat(data["updated_at"]), product.updated_at)
        self.assertIn("description", data)
        self.assertEqual(data["description"], product.description)
        self.assertIn("category", data)
        self.assertEqual(data["category"], product.category)
        self.assertIn("price", data)
        self.assertEqual(Decimal(str(data["price"])), product.price)
        self.assertIn("stock", data)
        self.assertEqual(data["stock"], product.stock)
        self.assertIn("image_url", data)
        self.assertEqual(data["image_url"], product.image_url)

    def test_deserialize_a_product(self):
        """It should de-serialize a Product"""
        data = ProductFactory().serialize()
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)

        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["description"], product.description)
        self.assertEqual(data["category"], product.category)
        self.assertEqual(Decimal(str(data["price"])), product.price)
        self.assertEqual(data["stock"], product.stock)
        self.assertEqual(data["image_url"], product.image_url)

    def test_deserialize_missing_name(self):
        """It should not deserialize a Product with a missing name"""
        data = {"id": 1, "category": "vegetables"}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_price(self):
        """It should not deserialize a negative price attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["price"] = -1.30
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_missing_required_attribute(self):
        """It should not deserialize dicts with a missing attribute"""
        for attr in ["name"]:
            test_product = ProductFactory()
            data = test_product.serialize()
            data.pop(attr, None)
            product = Product()
            self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_missing_optional_fields(self):
        """It should deserialize when optional fields are missing"""
        data = {"name": "Apple Pie"}

        product = Product()
        product.deserialize(data)

        self.assertIsNone(product.description)
        self.assertIsNone(product.category)
        self.assertIsNone(product.price)
        self.assertIsNone(product.stock)
        self.assertIsNone(product.image_url)
        self.assertEqual(product.name, "Apple Pie")

    def test_find_by_name(self):
        """It should find all products with the given name"""
        test_products = [ProductFactory() for _ in range(5)]
        for test_product in test_products:
            test_product.name = "Apple Pie"
            test_product.create()

        test_product_negative = ProductFactory()
        test_product_negative.name = "Apple"
        test_product_negative.create()

        self.assertEqual(len(Product.find_by_name("Apple Pie").all()), 5)


######################################################################
#  T E S T   A T T R I B U T E   V A L I D A T O R
######################################################################
class TestValidator(TestCaseBase):
    """test cases for the validator"""

    def test_validate_empty_name(self):
        """It should not validate a Product with an empty name"""
        product = ProductFactory()
        product.name = ""

        self.assertRaises(DataValidationError, product.validate)

    def test_validate_bad_name_type(self):
        """It should not validate a Product with a non-string name"""
        product = ProductFactory()
        product.name = [1, 2, 3]

        self.assertRaises(DataValidationError, product.validate)

    def test_validate_bad_description(self):
        """It should not validate a non-string description"""
        product = ProductFactory()
        product.description = 123

        self.assertRaises(DataValidationError, product.validate)

    def test_validate_bad_category(self):
        """It should not validate a non-string category"""
        product = ProductFactory()
        product.category = ["Food"]

        self.assertRaises(DataValidationError, product.validate)

    def test_validate_negative_price(self):
        """It should not validate a negative price"""
        product = ProductFactory()
        product.price = -1.99

        self.assertRaises(DataValidationError, product.validate)

    def test_validate_bad_price(self):
        """It should not validate a non-numeric price"""
        product = ProductFactory()
        product.price = "not-a-price"

        self.assertRaises(DataValidationError, product.validate)

    def test_validate_price_conversion(self):
        """It should convert a valid price to Decimal"""
        product = ProductFactory()
        product.price = 1.99

        product.validate()

        self.assertIsInstance(product.price, Decimal)
        self.assertEqual(product.price, Decimal("1.99"))

    def test_validate_negative_stock(self):
        """It should not validate negative stock"""
        product = ProductFactory()
        product.stock = -1

        self.assertRaises(DataValidationError, product.validate)

    def test_validate_bad_stock(self):
        """It should not validate non-numeric stock"""
        product = ProductFactory()
        product.stock = "many"

        self.assertRaises(DataValidationError, product.validate)

    def test_validate_bad_image_url(self):
        """It should not validate a non-string image URL"""
        product = ProductFactory()
        product.image_url = {"image": "https://example.com/image.jpg"}

        self.assertRaises(DataValidationError, product.validate)

    def test_validate_string_too_long(self):
        """It should not validate strings exceeding column length"""

        for field in ["name", "description", "category", "image_url"]:
            product = ProductFactory()

            max_length = Product.__table__.columns[field].type.length
            setattr(product, field, "x" * (max_length + 1))

            self.assertRaises(DataValidationError, product.validate)


######################################################################
#  T E S T   E X C E P T I O N   H A N D L E R S
######################################################################
class TestExceptionHandlers(TestCaseBase):
    """Product model exception handlers"""

    @patch("service.models.db.session.commit")
    def test_create_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.create)

    @patch("service.models.db.session.commit")
    def test_update_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.update)

    @patch("service.models.db.session.commit")
    def test_delete_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.delete)
