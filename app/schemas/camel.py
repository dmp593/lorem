import humps
import pydantic


class CamelModel(pydantic.BaseModel):
    class Config:
        alias_generator = humps.camelize
        allow_population_by_field_name = True
