from rest_framework.views import APIView
from rest_framework.response import Response
from django.test import TestCase
from pydantic import BaseModel, Field
from .types import *
from .utils import get_url_patterns
import pprint

from app1.api import AreaOfTriangleAPI


class APIAttributes(TestCase):

    """ Workings to test out looping through app urls and views
    """

    def test_get_urls(self):
        """ Get all URLS available for a given list of app names.
        """
        url_patterns = get_url_patterns(['app1', 'app2', 'app3'])
        print(url_patterns)

class DjaggerEndPointTest(TestCase):

    def test_from(self):

        ep = DjaggerEndPoint._from(AreaOfTriangleAPI, 'post')
        print(ep)

class DjaggerPathTest(TestCase):

    class ExampleAPI(APIView):

        def get(self, request, format=None):
            return Response({"msg":"Success"})

    def test_create(self):

        path = DjaggerPath.create(self.ExampleAPI)
        print(path.dict())

class DjaggerParameterTest(TestCase):
    """ Testing DjaggerParameter type
    """

    class ExampleBaseModel(BaseModel):
        name : str
        text : str = Field(
            default="default text", 
            description="text description"
        )
        
    def test_base_model_to_get_parameters(self):

        get_params = DjaggerParameter.model_to_get_parameters(self.ExampleBaseModel)
        self.assertEqual(len(get_params), 2)
        for param in get_params:
            self.assertTrue(isinstance(param, DjaggerParameter))
