import sys, os
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views import View
from .schemas import ExampleCBVGetQueryParams, ExampleCBVPostBodyParams

def example_fbv_view(request):
    """ Example function-based views API 
    """
    return JsonResponse({"foo":"bar"})


class CBVView(View):
    
    get_query_params = ExampleCBVGetQueryParams
    post_body_params = ExampleCBVPostBodyParams

    def get(self, request):
            # <view logic>
        return JsonResponse({"foo":"bar"})

    def post(self, request):

        return JsonResponse({"hello":"world"})