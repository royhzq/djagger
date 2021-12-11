from pydantic import BaseModel, Field


class ExampleCBVGetQueryParams(BaseModel):
    foo : str = Field(description="foo")

class ExampleCBVPostBodyParams(BaseModel):
    foo : str = Field(description="foo")

    @classmethod
    def example(cls):
        return cls(
            foo="Example post field value"
        )