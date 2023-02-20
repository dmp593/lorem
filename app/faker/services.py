import itertools

from faker import Faker
from typing import Any


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
        if '@each' not in schema:
            return { self.fake(key): self.fake(val) for key, val in schema.items() }

        each = schema.get('@each')
            
        schema = each.get('schema', {})
        count = each.get('count', 1)
        embeded = each.get('embeded', False)

        faked = []

        for _ in range(count):
            faked.append(self.fake(schema))

        if not embeded:
            return faked

        if isinstance(schema, list):
                return list(itertools.chain(*faked))
        
        if isinstance(schema, dict):
            output = {}

            for element in faked:
                output |= element
            
            return output

        return faked

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
