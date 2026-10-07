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

        if not isinstance(self.name, str):
            raise DataValidationError(f"name must be a string, got {type(self.name)}")

        if not self.name.strip():
            raise DataValidationError("name cannot be empty")

        if self.description is not None and not isinstance(self.description, str):
            raise DataValidationError(
                f"description must be a string, got {type(self.description)}"
            )

        if self.category is not None and not isinstance(self.category, str):
            raise DataValidationError(
                f"category must be a string, got {type(self.category)}"
            )

        if self.price is not None:
            try:
                self.price = Decimal(str(self.price))
            except (InvalidOperation, TypeError, ValueError) as error:
                raise DataValidationError("price must be a number") from error

            if self.price < 0:
                raise DataValidationError("price cannot be negative")

        if self.stock is not None:
            if isinstance(self.stock, bool) or not isinstance(
                self.stock, int
            ):  # True is int
                raise DataValidationError(
                    f"stock must be an integer, got {type(self.stock)}"
                )

            if self.stock < 0:
                raise DataValidationError("stock cannot be negative")

        if self.image_url is not None and not isinstance(self.image_url, str):
            raise DataValidationError(
                f"image_url must be a string, got {type(self.image_url)}"
            )

        for field in ["name", "description", "category", "image_url"]:
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
        # AttributeError handling seems unnecessary since we wouldn't deserialize non-exist attributes
        # except AttributeError as error:
        #     raise DataValidationError("Invalid attribute: " + error.args[0]) from error

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
