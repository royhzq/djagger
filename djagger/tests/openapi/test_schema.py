from pydantic import BaseModel

from ...enums import (
    HttpMethod
)

from ...openapi import (
    MediaType,
    Operation,
    Path,
    Document
)

def test_document():

    document = Document.generate(
        app_names=['djagger'],
        contact_email="example@example.com",
        contact_url="www.example.com"
    )
    print(document)

def test_media_type_from():

    class N(BaseModel):
        value3 : str

    class M(BaseModel):
        value1 : str
        value2 : str
        n : N

        @classmethod
        def example(cls):
            return cls(
                value1="value1",
                value2="value2",
                n=N(value3="value3")
            )

    media = MediaType._from(M, component="schemas")
    assert media.dict(by_alias=True)

def test_operation_from():

    class BodyParams(BaseModel):
        """ Test request body
        """
        value1 : str
        value2 : str

    class View():

        post_body_params = BodyParams

        def post(self):
            return None
    
    operation = Operation._from(View, HttpMethod('post'))
    assert operation.dict(by_alias=True)

def test_path_create():

    class BodyParams(BaseModel):
        """ Test request body
        """
        value1 : str
        value2 : str

    class ResponseSchema(BaseModel):
        """ Test response schema
        """
        msg: str

    class View():

        post_body_params = BodyParams
        response_schema = {
            "200":ResponseSchema,
            "400":ResponseSchema
        }

        def post(self):
            return None

    path = Path.create(View)

    print(path.dict(by_alias=True, exclude_none=True))
    assert path.dict(by_alias=True)
