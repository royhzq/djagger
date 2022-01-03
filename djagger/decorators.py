"""
Decorators
==========
"""
from typing import List
from .enums import HttpMethod, ViewAttributes, DJAGGER_HTTP_METHODS
import warnings


def schema(methods: List[str], **attrs):
    """Decorator for function based views to set Djagger attributes into the view.
    A list of http method strings are needed to inform Djagger which endpoint schemas to create
    I.e. ``GET`` ``POST`` ``PUT`` ``PATCH`` ``DELETE``

    Example::

        @schema(
            methods=["GET", "POST"],
            summary="My FBV Endpoint",
            get_response_schema=MyFBVResponseSchema
        )
        def my_fb_view(request):
            # Your code logic
            return JsonResponse({"foo":"bar"})

    """

    def decorator(f):

        for k, v in attrs.items():
            if k not in ViewAttributes.attr_list:
                warnings.warn(f"schema decorator got an unexpected keyword {k}")
                continue
            setattr(f, k, v)

        # Validate http method strings
        for method in methods:
            try:
                HttpMethod(method.lower())
            except ValueError:
                raise ValueError(f"methods must be a list of string http methods e.g., {HttpMethod.values()}")
        
        # Save the http methods used in the fbv as an attribute
        setattr(f, DJAGGER_HTTP_METHODS, methods)

        return f

    return decorator
