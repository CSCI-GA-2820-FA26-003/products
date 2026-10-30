"""
Models for Product

All of the models are stored in this module
"""

from decimal import Decimal, InvalidOperation
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors"""


class Product(db.Model):
    """
    Class that represents a Product
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    description = db.Column(db.String(256))
    category = db.Column(db.String(63))

    price = db.Column(db.Numeric(10, 2))

    stock = db.Column(db.Integer)

    image_url = db.Column(db.String(512))

    def validate(self):
        """Validates the product data."""
        self._validate_name()
        self._validate_optional_strings()
        self._validate_price()
        self._validate_stock()
        self._validate_string_lengths()

    def _validate_name(self):
        """Validates the product name."""
        if not isinstance(self.name, str):
            raise DataValidationError(f"name must be a string, got {type(self.name)}")

        if not self.name.strip():
            raise DataValidationError("name cannot be empty")

    def _validate_optional_strings(self):
        """Validates optional string fields."""
        for field in ("description", "category", "image_url"):
            value = getattr(self, field)
            if value is not None and not isinstance(value, str):
                raise DataValidationError(
                    f"{field} must be a string, got {type(value)}"
                )

    def _validate_price(self):
        """Validates the product price."""
        if self.price is not None:
            try:
                self.price = Decimal(str(self.price))
            except (InvalidOperation, TypeError, ValueError) as error:
                raise DataValidationError("price must be a number") from error

            if self.price < 0:
                raise DataValidationError("price cannot be negative")

    def _validate_stock(self):
        """Validates the product stock."""
        if self.stock is not None:
            if isinstance(self.stock, bool) or not isinstance(self.stock, int):
                raise DataValidationError(
                    f"stock must be an integer, got {type(self.stock)}"
                )

            if self.stock < 0:
                raise DataValidationError("stock cannot be negative")

    def _validate_string_lengths(self):
        """Validates string field lengths."""
        for field in ("name", "description", "category", "image_url"):
            value = getattr(self, field)
            if value is not None:
                max_length = self.__table__.columns[field].type.length
                if max_length is not None and len(value) > max_length:
                    raise DataValidationError(
                        f"{field} cannot exceed {max_length} characters"
                    )

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s", self.name)
        self.validate()
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Product to the database
        """
        logger.info("Saving %s", self.name)
        self.validate()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def purchase(self):
        """Purchase a single unit, decrementing the stock.

        Raises:
            DataValidationError: when the product is out of stock
        """
        logger.info("Purchasing %s", self.name)
        if self.stock is None or self.stock <= 0:
            raise DataValidationError("Product is out of stock")

        self.stock -= 1
        self.update()

    def delete(self):
        """Removes a Product from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Product into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": (
                self.created_at.isoformat() if self.created_at is not None else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at is not None else None
            ),
            "description": self.description,
            "category": self.category,
            "price": str(self.price) if self.price is not None else None,
            "stock": self.stock,
            "image_url": self.image_url,
        }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.description = data.get("description", None)
            self.category = data.get("category", None)
            self.price = data.get("price", None)
            self.stock = data.get("stock", None)
            self.image_url = data.get("image_url", None)
            self.validate()

        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Products in the database"""
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Product by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_price_range(cls, min_price=None, max_price=None):
        """Returns all Products with a price between min_price and max_price"""
        logger.info(
            "Processing price range query for %s to %s ...", min_price, max_price
        )
        query = cls.query
        if min_price is not None:
            query = query.filter(cls.price >= min_price)
        if max_price is not None:
            query = query.filter(cls.price <= max_price)
        return query
