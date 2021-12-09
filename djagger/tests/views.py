
from django.http import JsonResponse, HttpRequest, HttpResponse
from ..decorators import schema
from .schemas import ExampleFBVGetQueryParams, ExampleFBVPostBodyParams

@schema(
    methods=['GET', 'Post'], 
    get_query_params=ExampleFBVGetQueryParams,
    post_body_params=ExampleFBVPostBodyParams
)
def example_fbv_view(request):
    """ Example function-based views API 
    """
    return JsonResponse({"foo":"bar"})

