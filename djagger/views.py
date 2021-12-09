from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import os
import json

from .utils import *
from .types import *
from app1.api import ListItemsAPI, AreaOfTriangleAPI, AreaOfTriangleRequest, AreaOfTriangleResponse


# Create your views here.
def api_doc(request):

  return render(request, 'OpenAPI/redoc.html')

def pet_store_json(request):

    with open(os.path.join(settings.BASE_DIR, 'templates/OpenAPI/pet_store.json')) as f:
        data = json.loads(f.read())

    return JsonResponse(data)

class ExampleGetParameterType(BaseModel):
    """ Example GET request parameter i.e. /api/items/list/<item_id>
    """
    item_id : str

class ExampleGetResponseType(BaseModel):
    """ Example GET 200 response type
    """
    items : List[str]

    @classmethod
    def example(cls):
        return cls(items=["item A", "item B", "item C"])

def open_api_json(request):
    
    document = DjaggerDoc.generate_openapi(
        app_names=['app1', 'app2'], 
        description="",
        contact_name = "Roy Hung",
        contact_email = "royhung@protonmail.com",
        contact_url = "www.example.org",
        license_name="Apache 2.0",
        license_url="http://www.apache.org/licenses/LICENSE-2.0.html",
        basePath="/V2",
        tags = [
            {"name":"My Tag", "description":"eeml"}
        ]
    )
    response = JsonResponse(document)
    response['Cache-Control'] = "no-cache, no-store, must-revalidate"
    return response