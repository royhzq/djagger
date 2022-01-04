from rest_framework import serializers
from pydantic import BaseModel
from ..generics import set_response_schema_from_serializer_class


def test_set_response_schema_from_serializer_class_1():

    # Test successful setting of response schema from serializer_class

    class TestSerializer(serializers.Serializer):
        field = serializers.CharField()

    class TestView:
        serializer_class = TestSerializer

    set_response_schema_from_serializer_class(TestView)

    assert TestView.response_schema == TestView.serializer_class


def test_set_response_schema_from_serializer_class_2():

    # Test skipping setting of response schema from serializer_class
    # when serializer_class is not of the correct type

    class TestSerializer(serializers.Serializer):
        field = serializers.CharField()

    class TestView:
        serializer_class = None

    set_response_schema_from_serializer_class(TestView)

    assert not hasattr(TestView, "response_schema")


def test_set_response_schema_from_serializer_class_3():

    # Test skipping setting of response schema from serializer_class
    # when response_schema is already set

    class TestResponseSchema(BaseModel):
        field2: str

    class TestSerializer(serializers.Serializer):
        field = serializers.CharField()

    class TestView:
        serializer_class = TestSerializer
        response_schema = TestResponseSchema

    set_response_schema_from_serializer_class(TestView)

    assert TestView.response_schema == TestResponseSchema
