from typing import Any
from faker import Faker
from app.core import exceptions

from app.faker.schemas import FakerSchema


class FakerService:
    def __init__(self, locale = "en_US"):
        self.faker = Faker(locale=locale)

    def fake(self, schema: FakerSchema) -> list[any]:
        faked = []

        for i in range(schema.size):
            faked.append({})

            for item in schema.fake:
                if item == "fake" or not hasattr(self, item):
                    raise exceptions.BadRequest(f"Faker: can't provide a faked value for item '{item}'")

                faked[i][item] = getattr(self, item)()

        return faked

    def __getattr__(self, __name: str) -> Any:
        return getattr(self.faker, __name)