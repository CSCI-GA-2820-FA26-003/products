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
TestProduct API Service Test Suite
"""

# pylint: disable=duplicate-code
from decimal import Decimal
import os
import json
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Product
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Products Service")
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(data["list_url"], "/products")

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_product(self):
        """It should Update an existing Product"""
        # create a product to update
        test_product = ProductFactory()
        test_product.create()

        # update the product
        new_product = ProductFactory()
        new_product.id = test_product.serialize()["id"]
        logging.debug(new_product)
        response = self.client.put(
            f"{BASE_URL}/{new_product.id}", json=new_product.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["name"], new_product.name)
        self.assertEqual(updated_product["description"], new_product.description)
        self.assertEqual(updated_product["category"], new_product.category)
        self.assertEqual(Decimal(str(updated_product["price"])), new_product.price)
        self.assertEqual(updated_product["stock"], new_product.stock)
        self.assertEqual(updated_product["image_url"], new_product.image_url)

    def test_update_bad_id(self):
        """It should not update a Product if id does not exist"""
        # create a product to update
        test_product = ProductFactory()
        test_product.id = 99999

        # update the product
        response = self.client.put(f"{BASE_URL}/99999", json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST TOOLS
    # ----------------------------------------------------------
    def test_update_without_content_type(self):
        """It should return 415 when Content-Type is missing"""
        response = self.client.put(
            f"{BASE_URL}/1",
            data=json.dumps({"name": "Updated Product"}),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    def test_update_with_invalid_content_type(self):
        """It should return 415 for an unsupported Content-Type"""
        response = self.client.put(
            f"{BASE_URL}/1",
            data=json.dumps({"name": "Updated Product"}),
            content_type="text/plain",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )
