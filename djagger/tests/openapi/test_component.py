from pydantic import BaseModel
from ...openapi import Components


def test_component_extraction():

    class N(BaseModel):
        value3 : str

    class M(BaseModel):
        value1 : str
        value2 : str
        n : N
    schema = Components.extract_component_schema(M, "schemas")
    assert schema.get('component')
    print(schema)