"""
Enums
=====
"""
from typing import Union, List
from enum import Enum
from .utils import djagger_method_enum_factory

DJAGGER_HTTP_METHODS = 'djagger_http_methods' # FBV attribute name for http methods used in the FBV


class DjaggerAPIAttributes(str, Enum):
    """Available API-level openAPI attributes that can be set in the view.

    API-level attributes listed here that are initialized in the view will apply to all http method endpoints
    withinin the view, unless an endpoint-specific attribute exists which will override the api-level attribute.
    """ 
    SUMMARY = 'summary'
    TAGS = 'tags'
    DESCRIPTION = 'description'
    CONSUMES = 'consumes'
    PRODUCES = 'produces'
    DJAGGER_EXCLUDE = 'djagger_exclude' # If attr is present and True in view, skip documenting the view


### Enums of endpoint attributes available for each http method ###

DjaggerGetAttributes = djagger_method_enum_factory("DjaggerGetAttributes", "get")
DjaggerPostAttributes = djagger_method_enum_factory("DjaggerPostAttributes", "post")
DjaggerPatchAttributes = djagger_method_enum_factory("DjaggerPatchAttributes", "patch")
DjaggerDeleteAttributes = djagger_method_enum_factory("DjaggerDeleteAttributes", "delete")
DjaggerPutAttributes = djagger_method_enum_factory("DjaggerPutAttributes", "put")

###

DjaggerMethodAttributes = Union[
    DjaggerGetAttributes, 
    DjaggerPostAttributes, 
    DjaggerPatchAttributes, 
    DjaggerPutAttributes, 
    DjaggerDeleteAttributes
]

# List of all allowable djagger attribute names for a given view
DjaggerViewAttributeList : List[str] = [
    *[ member.value for member in list(DjaggerAPIAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerGetAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerPostAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerPatchAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerDeleteAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerPutAttributes.__members__.values())],
]

class HttpMethod(str, Enum):
    GET = 'get'
    POST = 'post'
    PATCH = 'patch'
    DELETE = 'delete'
    PUT = 'put'

    def to_djagger_attribute(self) -> 'DjaggerMethodAttributes':
        """ Returns the corresponding DjaggerMethodAttribute depending on
        the http method
        """ 
        if self == self.GET:
            return DjaggerGetAttributes
        elif self == self.POST:
            return DjaggerPostAttributes
        elif self == self.PATCH:
            return DjaggerPatchAttributes
        elif self == self.DELETE:
            return DjaggerDeleteAttributes
        elif self == self.PUT:
            return DjaggerPutAttributes
        
class ParameterLocation(str, Enum):
    """ OpenAPI parameter locations. The values of `in` for parameter object.
    """
    QUERY = 'query'
    HEADER = 'header'
    PATH = 'path'
    COOKIE = 'cookie'
    BODY = 'body'
    FORM = 'formData'

    @classmethod
    def from_method_attribute(cls, attr : 'DjaggerMethodAttributes') -> 'ParameterLocation':
        """ Returns an instance of itself with the location inferred from DjaggerMethodATtibutes 
        """
        if attr == attr.PATH_PARAMS:
            return cls.PATH
        elif attr == attr.QUERY_PARAMS:
            return cls.QUERY
        elif attr == attr.HEADER_PARAMS:
            return cls.HEADER
        elif attr == attr.COOKIE_PARAMS:
            return cls.COOKIE
        elif attr == attr.BODY_PARAMS:
            return cls.BODY
        elif attr == attr.FORM_PARAMS:
            return cls.FORM
        else:
            return None