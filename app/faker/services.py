from typing import Any
from faker import Faker


class FakerService:
    def __init__(self, locale = "en_US"):
        self.faker = Faker(locale=locale)

    @property
    def username(self) -> str:
        return self.faker.simple_profile.username()

    def __getattr__(self, __name: str) -> Any:
        return getattr(self.faker, __name)()

    def fake_list(self, schema: list) -> list:
        elements = []

        for element in schema:
            faked_element = self.fake(element)

            if isinstance(faked_element, list):
                for fe in faked_element:
                    elements.append(fe)
            else:
                elements.append(faked_element)

        return elements

    def fake_dict(self, schema: dict) -> dict | list:
        if '@each' in schema:
            each = schema.get('@each')
            schema = each.get('schema', {})
            count = each.get('count', 1)

            return self.fake_list([schema for _ in range(count)])
        
        return { self.fake(key): self.fake(val) for key, val in schema.items() }

    def fake(self, schema: any) -> any:
        if isinstance(schema, str) and schema.startswith('@'):
            paths = schema[1:].split('.')

            value = getattr(self, paths[0])

            for path in paths[1:]:
                value = value.get(path)

            return value

        if isinstance(schema, list):
            return self.fake_list(schema)

        if isinstance(schema, dict):
            return self.fake_dict(schema)

        return schema
