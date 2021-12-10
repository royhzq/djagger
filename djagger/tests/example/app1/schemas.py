from pydantic import BaseModel, Field


class ExampleFBVGetQueryParams(BaseModel):
    foo : str = Field(description="foo")

class ExampleFBVPostBodyParams(BaseModel):
    foo : str = Field(description="foo")