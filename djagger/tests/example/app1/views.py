import sys, os
from django.http import JsonResponse, HttpRequest, HttpResponse
from .schemas import ExampleFBVGetQueryParams, ExampleFBVPostBodyParams


def example_fbv_view(request):
    """ Example function-based views API 
    """
    return JsonResponse({"foo":"bar"})

