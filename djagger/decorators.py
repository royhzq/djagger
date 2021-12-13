from typing import List
from .enums import HttpMethod, DjaggerViewAttributeList, DJAGGER_HTTP_METHODS

def schema(methods : List[str], **attrs):
    """ Decorator for function based views to set Djagger attributes into the view.
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
            if k not in DjaggerViewAttributeList:
                raise TypeError(f'schema decorator got an unexpected keyword {k}')
            setattr(f, k, v)

        # Save the http methods used in the fbv as an attribute
        setattr(f, DJAGGER_HTTP_METHODS, methods)

        return f
    return decorator