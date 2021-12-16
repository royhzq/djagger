from pydantic import BaseModel
from rest_framework import serializers, fields
from typing import List
from ...enums import HttpMethod

from ...schema import (
    DjaggerEndPoint
)

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


def test_extract_paramaters_fallback():
    
    # Fallback to api-level param attribute if 
    # method-level param attribute does not exist

    class BodyParams(BaseModel):
        """BodyParams"""
        field_1 : str
        field_2 : int

    class PostBodyParams(BaseModel):
        """PostBodyParams"""
        field_3 : str
        filed_4 : int

    class View:
        body_params = BodyParams
        post_body_params = PostBodyParams

    class View2:
        body_params = BodyParams

    # View post body params should be utilizing `PostBodyParams`
    endpoint = DjaggerEndPoint()
    endpoint._extract_parameters(view=View, http_method=HttpMethod('post'))
    assert len(endpoint.parameters) == 1
    assert endpoint.parameters[0].description == PostBodyParams.__doc__

    # View2 post body params should be utilizing `BodyParams`
    endpoint = DjaggerEndPoint()
    endpoint._extract_parameters(view=View2, http_method=HttpMethod('post'))
    assert len(endpoint.parameters) == 1
    assert endpoint.parameters[0].description == BodyParams.__doc__
    

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

def test_extract_responses_fallback():
    
    # Fallback to api-level response schema attribute if 
    # method-level response schema attribute does not exist

    class SchemaResponse(BaseModel):
        """SchemaResponse"""
        field_1 : str
        field_2 : int

    class PutSchemaResponse(BaseModel):
        """PutSchemaResponse"""
        field_3 : str
        filed_4 : int

    class View:
        response_schema = SchemaResponse
        put_response_schema = PutSchemaResponse

    class View2:
        response_schema = SchemaResponse

    # View put response  should be utilizing `PutSchemaResponse`
    endpoint = DjaggerEndPoint()
    endpoint._extract_responses(view=View, http_method=HttpMethod('put'))
    assert len(endpoint.responses) == 1
    assert endpoint.responses['200'].description == PutSchemaResponse.__doc__

    # View2 put response  should be utilizing `SchemaResponse`
    endpoint = DjaggerEndPoint()
    endpoint._extract_responses(view=View2, http_method=HttpMethod('put'))
    assert len(endpoint.responses) == 1
    assert endpoint.responses['200'].description == SchemaResponse.__doc__
    