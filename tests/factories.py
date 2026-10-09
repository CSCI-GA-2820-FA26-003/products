"""
Test Factory to make fake objects for testing
"""

import factory
from faker import Faker
from service.models import Product

faker = Faker()


class ProductFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    # id = factory.Sequence(lambda n: n)
    name = factory.LazyFunction(
        lambda: " ".join(faker.words(nb=faker.random_int(min=1, max=3))).title()
    )
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    description = factory.Faker("sentence")
    category = factory.Faker("word")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    stock = factory.Faker("random_int", min=0, max=100)
    image_url = factory.Faker("url")
