from pydantic import BaseModel
from rest_framework import serializers, fields
from typing import List
from ..enums import HttpMethod

from ..schema import (
    DjaggerInfo, 
    DjaggerLogo, 
    DjaggerExternalDocs, 
    DjaggerTag,
    DjaggerContact, 
    DjaggerLicense,
    DjaggerEndPoint
)

def test_djagger_logo():
    data = DjaggerLogo(
        url="https://example.org/image.png", 
        altText="Test logo image"
    ).dict()

    assert data

def test_djagger_external_docs():
    data = DjaggerExternalDocs(
        description="test description",
        url="URL of description"
    ).dict()
    assert data


def test_djagger_tag():
    data = DjaggerTag(
        name="Tag name",
        description = "description",
        externalDocs = DjaggerExternalDocs(
            description="test description",
            url="URL description"
        )
    ).dict()
    assert data

def test_djagger_contact():
    data = DjaggerContact(
        name="Test Name",
        url="Test URL",
        email="example@example.org"
    ).dict()
    assert data

def test_djagger_license():
    data = DjaggerLicense(
        name="test license name",
        url="license Url"
    ).dict()
    assert data

def test_djagger_info():

    data = DjaggerInfo(
        description = "Test Info Description",
        version = "2.0",
        title = "Test Djagger Info",
        termsOfService = "Reference to ToS",
        contact = DjaggerContact(),
        x_logo=DjaggerLogo(),
    ).dict(by_alias=True)
    assert data
    assert data.get('x-logo')


def test_extract_parameters():

    class GetParams(BaseModel):
        value1 : str
        value2 : int

    class View:
        get_path_params = GetParams

    endpoint = DjaggerEndPoint()
    endpoint._extract_parameters(view=View, http_method=HttpMethod('get'))
    assert len(endpoint.parameters) == 2 # value1 and value2 attr

def test_extract_parameters_from_serializer():

    class GetSerializer(serializers.Serializer):
        value1 = fields.CharField()
        value2 = fields.IntegerField()

    class View:
        get_path_params = GetSerializer

    endpoint = DjaggerEndPoint()
    endpoint._extract_parameters(view=View, http_method=HttpMethod('get'))
    assert len(endpoint.parameters) == 2 # value1 and value2 attr

def test_extract_responses():

    class GetResponse(BaseModel):
        value1 : str
        value2 : int

    class View:
        get_response_schema = GetResponse

    endpoint = DjaggerEndPoint()
    endpoint._extract_responses(view=View, http_method=HttpMethod('get'))
    assert len(endpoint.responses) == 1 

def test_extract_multiple_responses():

    class GetResponse(BaseModel):
        value1 : str
        value2 : int

    class ErrorResponse(BaseModel):
        errors : List[str]

    class View:
        get_response_schema = {
            '200': GetResponse,
            '400': ErrorResponse
        }

    endpoint = DjaggerEndPoint()
    endpoint._extract_responses(view=View, http_method=HttpMethod('get'))
    assert len(endpoint.responses) == 2

def test_extract_responses_from_serializer():

    class GetSerializer(serializers.Serializer):
        value1 = fields.CharField()
        value2 = fields.IntegerField()

    class View:
        get_response_schema = GetSerializer

    endpoint = DjaggerEndPoint()
    endpoint._extract_responses(view=View, http_method=HttpMethod('get'))
    assert len(endpoint.responses) == 1 


def test_extract_multiple_responses_from_serializer():

    class GetSerializer(serializers.Serializer):
        value1 = fields.CharField()
        value2 = fields.IntegerField()

    class ErrorSerializer(serializers.Serializer):
        errors = fields.ListField(child=fields.CharField())

    class View:
        get_response_schema = {
            '200':GetSerializer,
            '400':ErrorSerializer
        }
    endpoint = DjaggerEndPoint()
    endpoint._extract_responses(view=View, http_method=HttpMethod('get'))
    assert len(endpoint.responses) == 2