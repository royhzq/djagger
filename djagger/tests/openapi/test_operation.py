from pydantic import BaseModel
from rest_framework import serializers
from ...openapi import Operation, ExternalDocs, Server, RequestBody, MediaType, Response
from ...enums import HttpMethod


def test_extract_summary():

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_summary(View, HttpMethod.GET)

    assert operation.summary == "View"  # View.__name__

    # 2. Use API-level attribute
    class View:
        summary = "value1"

    operation = Operation()
    operation._extract_summary(View, HttpMethod.GET)

    assert operation.summary == View.summary

    # 3. Use operation-level attribute as priority
    class View:
        get_summary = "value1"
        summary = "value2"

    operation = Operation()
    operation._extract_summary(View, HttpMethod.GET)

    assert operation.summary == View.get_summary


def test_extract_description():

    # 1. No attribute
    class View:
        """This is the View docstring"""

        ...

    operation = Operation()
    operation._extract_description(View, HttpMethod.GET)

    assert operation.description == View.__doc__

    # 2. Use API-level attribute
    class View:
        description = "value1"

    operation = Operation()
    operation._extract_description(View, HttpMethod.GET)

    assert operation.description == View.description

    # 3. Use operation-level attribute as priority
    class View:
        get_description = "value1"
        description = "value2"

    operation = Operation()
    operation._extract_description(View, HttpMethod.GET)

    assert operation.description == View.get_description


def test_extract_operation_id():

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_operation_id(View, HttpMethod.GET)

    assert operation.operationId == None

    # 2. Use API-level attribute
    class View:
        operation_id = "value1"

    operation = Operation()
    operation._extract_operation_id(View, HttpMethod.GET)

    assert operation.operationId == View.operation_id

    # 3. Use operation-level attribute as priority
    class View:
        get_operation_id = "value1"
        operation_id = "value2"

    operation = Operation()
    operation._extract_operation_id(View, HttpMethod.GET)

    assert operation.operationId == View.get_operation_id


def test_extract_deprecated():

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_deprecated(View, HttpMethod.GET)

    assert operation.deprecated == None

    # 2. Use API-level attribute
    class View:
        deprecated = True

    operation = Operation()
    operation._extract_deprecated(View, HttpMethod.GET)

    assert operation.deprecated == View.deprecated

    # 3. Use operation-level attribute as priority
    class View:
        get_deprecated = True
        deprecated = False

    operation = Operation()
    operation._extract_deprecated(View, HttpMethod.GET)

    assert operation.deprecated == View.get_deprecated


def test_extract_tags():

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_tags(View, HttpMethod.GET)

    assert operation.tags == [View.__module__.split(".")[0]]

    # 2. Use API-level attribute
    class View:
        tags = ["app1", "app2"]

    operation = Operation()
    operation._extract_tags(View, HttpMethod.POST)
    assert operation.tags == View.tags

    # 3. Use API-level attribute
    class View:
        tags = ["app3", "app4"]
        post_tags = ["app1", "app2"]

    operation = Operation()
    operation._extract_tags(View, HttpMethod.POST)
    assert operation.tags == View.post_tags


def test_extract_external_docs():

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_external_docs(View, HttpMethod.GET)

    assert operation.externalDocs == None

    # 2. Use API-level attribute
    class View:
        external_docs = {"url": "https://example.org"}

    operation = Operation()
    operation._extract_external_docs(View, HttpMethod.POST)
    assert operation.externalDocs == ExternalDocs.parse_obj(View.external_docs)

    # 3. Use operation-level attribute
    class View:
        external_docs = {"url": "https://example.org"}
        post_external_docs = {"url": "https://test.org"}

    operation = Operation()
    operation._extract_external_docs(View, HttpMethod.POST)
    assert (
        operation.externalDocs.url
        == ExternalDocs.parse_obj(View.post_external_docs).url
    )


def test_extract_servers():

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_servers(View, HttpMethod.GET)

    assert operation.servers == None

    # 2. Use API-level attribute
    class View:
        servers = [{"url": "https://example.org"}]

    operation = Operation()
    operation._extract_servers(View, HttpMethod.POST)
    assert operation.servers == [Server.parse_obj(server) for server in View.servers]

    # 3. Use operation-level attribute
    class View:
        servers = [{"url": "https://example.org"}]
        post_servers = [{"url": "https://test.org"}]

    operation = Operation()
    operation._extract_servers(View, HttpMethod.POST)
    assert operation.servers == [
        Server.parse_obj(server) for server in View.post_servers
    ]


def test_extract_security():

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_security(View, HttpMethod.GET)

    assert operation.servers == None

    # 2. Use API-level attribute
    class View:
        security = [{"security1": ["value1", "value2"]}]

    operation = Operation()
    operation._extract_security(View, HttpMethod.POST)
    assert operation.security == View.security

    # 3. Use operation-level attribute
    class View:
        security = [{"security1": ["value1", "value2"]}]
        post_security = [{"security2": ["value3", "value4"]}]

    operation = Operation()
    operation._extract_security(View, HttpMethod.POST)
    assert operation.security == View.post_security


def test_extract_request_body():
    class Params(BaseModel):
        """Request body params"""

        field1: str
        field2: int

    class PostParams(BaseModel):
        """Specific operation level body params"""

        field3: str

    class TestSerializer(serializers.Serializer):
        """Test Serializer"""

        field4 = serializers.IntegerField()

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_request_body(View, HttpMethod.POST)

    assert operation.requestBody == None

    # 2. Use API-level attribute
    class View:
        request_schema = Params

    operation = Operation()
    operation._extract_request_body(View, HttpMethod.POST)
    assert isinstance(operation.requestBody, RequestBody)

    # 3. Use operation-level attribute
    class View:
        request_schema = Params
        post_request_schema = PostParams

    operation = Operation()
    operation._extract_request_body(View, HttpMethod.POST)
    assert isinstance(operation.requestBody, RequestBody)
    assert operation.requestBody.description == PostParams.__doc__

    # 3.5 - User operation-level attribute with serializer
    class View:
        request_schema = TestSerializer
        post_request_schema = TestSerializer

    operation = Operation()
    operation._extract_request_body(View, HttpMethod.POST)
    assert isinstance(operation.requestBody, RequestBody)
    assert operation.requestBody.description == TestSerializer.__doc__

    # 4 . Case where a dict of multiple request bodies passed

    class View:
        request_schema = {
            "application/json": Params,
            "text/plain": PostParams,
            "text/html": TestSerializer,
        }

    operation = Operation()
    operation._extract_request_body(View, HttpMethod.POST)
    assert isinstance(operation.requestBody, RequestBody)
    assert operation.requestBody.content
    for media in operation.requestBody.content.values():
        assert isinstance(media, MediaType)

    # 5 . Case where a dict of multiple request bodies passed
    # and dicts are used instead of pydantic modes

    class View:
        request_schema = {
            "application/json": {
                "schema": {
                    "title": "custom schema",
                    "type": "string",
                    "description": "some description",
                }
            }
        }

    operation = Operation()
    operation._extract_request_body(View, HttpMethod.POST)
    assert isinstance(operation.requestBody, RequestBody)
    assert operation.requestBody.content
    for media in operation.requestBody.content.values():
        assert isinstance(media, MediaType)


def test_extract_responses():
    class ResponseSchema(BaseModel):
        field: str

        @classmethod
        def example(cls):
            return cls(field="response schema example")

    class PostResponseSchema(BaseModel):
        field2: int

    class ErrorSchema(BaseModel):
        message: str

    class TestSerializer(serializers.Serializer):
        """Test Serializer"""

        field3 = serializers.IntegerField()

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_responses(View, HttpMethod.POST)

    assert operation.requestBody == None

    # 2. Use API-level attribute
    class View:
        response_schema = ResponseSchema

    operation = Operation()
    operation._extract_responses(View, HttpMethod.POST)
    assert isinstance(operation.responses.get("200"), Response)

    # 3. Use API-level attribute
    class View:
        post_response_schema = PostResponseSchema
        response_schema = ResponseSchema

    operation = Operation()
    operation._extract_responses(View, HttpMethod.POST)
    assert operation.responses.get("200")

    # 3.5 Use API-level attribute with serializers
    class View:
        post_response_schema = TestSerializer
        response_schema = TestSerializer

    operation = Operation()
    operation._extract_responses(View, HttpMethod.POST)
    assert operation.responses.get("200")

    # 4. Multiple responses
    class View:
        post_response_schema = {
            "200": PostResponseSchema,
            "400": ErrorSchema,
            "404": TestSerializer,
        }

    operation = Operation()
    operation._extract_responses(View, HttpMethod.POST)
    assert operation.responses.get("200")
    assert operation.responses.get("400")
    assert operation.responses.get("404")

    # 5. Multiple responses with non-default content type
    class View:
        post_response_schema = {
            ("200", "application/json"): PostResponseSchema,
            ("400", "text/plain"): ErrorSchema,
            ("404", "application/octet-stream"): TestSerializer,
        }

    operation = Operation()
    operation._extract_responses(View, HttpMethod.POST)

    assert operation.responses.get("200")
    assert operation.responses.get("400")
    assert operation.responses.get("404")

    assert "application/json" in operation.responses["200"].content.keys()
    assert "text/plain" in operation.responses["400"].content.keys()
    assert "application/octet-stream" in operation.responses["404"].content.keys()


def test_extract_parameters():

    # 1. No attribute
    class View:
        ...

    operation = Operation()
    operation._extract_parameters(View, HttpMethod.GET)
    assert operation.parameters == []

    # 2. Path and query params
    class PathParams(BaseModel):
        pk: int
        name: str

    class QueryParams(BaseModel):
        page: int

    class TestSerializer(serializers.Serializer):
        """Test Serializer"""

        field1 = serializers.IntegerField()
        field2 = serializers.CharField()

    # 1. Test query and path parameters
    class View:
        path_params = PathParams
        query_params = QueryParams

    operation = Operation()
    operation._extract_parameters(View, HttpMethod.GET)

    # 1.5 - Test query and path parameters with serializers

    class View:
        path_params = TestSerializer
        query_params = TestSerializer

    operation = Operation()
    operation._extract_parameters(View, HttpMethod.GET)
