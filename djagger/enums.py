"""
Enums
=====
"""
from typing import Union, List, Any, Type
from enum import Enum

DJAGGER_HTTP_METHODS = 'djagger_http_methods' # FBV attribute name for http methods used in the FBV


class DjaggerAPIAttributes(str, Enum):
    """Available API-level openAPI attributes that can be set in the view.

    API-level attributes listed here that are initialized in the view will apply to all http method endpoints
    withinin the view, unless an endpoint-specific attribute exists which will override the api-level attribute.
    """ 

    PATH_PARAMS = 'path_params'
    QUERY_PARAMS = 'query_params'
    HEADER_PARAMS = 'header_params'
    COOKIE_PARAMS = 'cookie_params'
    BODY_PARAMS = 'body_params'
    RESPONSE_SCHEMA = 'response_schema'

    SUMMARY = 'summary'
    TAGS = 'tags'
    DESCRIPTION = 'description'
    CONSUMES = 'consumes'
    PRODUCES = 'produces'
    OPERATION_ID = 'operation_id'
    DEPRECATED = 'deprecated'
    EXTERNAL_DOCS = 'external_docs'
    SERVERS = 'servers'
    SECURITY = 'security'
    DJAGGER_EXCLUDE = 'djagger_exclude' # If attr is present and True in view, skip documenting the view

    def from_view(self, view: Type, http_method : 'HttpMethod') -> Any:

        """ Given a view, and a http method, extracts the attribute from the view starting at the operation-level attribute i.e. get_body_params.
        If it does not exist, try to extract at the API-level attribute i.e. body_params.
        If the attribute still does not exist, return None.

        Example::
            >>>DjaggerAPIAttributes.OPERATION_ID.from_view(view, HttpMethod.GET)
            "get_operation_id"

        """
        operation_attr_value = f"{http_method.value}_{self.value}" # e.g. get_body_params
        return getattr(view, operation_attr_value, getattr(view, self.value, None))


    @classmethod
    def items(cls):
        """ List of tuples of the enum attr names and the corresponding value"""
        return [ (k, v.value) for k, v in cls.__members__.items() ]

    @classmethod
    def operation_factory(cls, name: str, method : str) -> Enum:

        """ Factory generate DjaggerMethodAttributes enums that 
        represent the allowable attributes for setting request and response schema objects
        in a view for a particular http method.

        Args:
            name (str): The name of the Enum class that will be created. 
            method (str): The http method name i.e. 'get', 'post', 'put', 'patch'. 
                        `method` will be prefixed to all the enum values upon creation.
        """
    
        prefixed_attrs = { k: f"{method}_{v}" for k, v in cls.items() } 

        return Enum(name, prefixed_attrs)

### Enums of endpoint attributes available for each http method ###

DjaggerGetAttributes = DjaggerAPIAttributes.operation_factory("DjaggerGetAttributes", "get")
DjaggerPostAttributes = DjaggerAPIAttributes.operation_factory("DjaggerPostAttributes", "post")
DjaggerPatchAttributes = DjaggerAPIAttributes.operation_factory("DjaggerPatchAttributes", "patch")
DjaggerDeleteAttributes = DjaggerAPIAttributes.operation_factory("DjaggerDeleteAttributes", "delete")
DjaggerPutAttributes = DjaggerAPIAttributes.operation_factory("DjaggerPutAttributes", "put")
DjaggerOptionsAttributes = DjaggerAPIAttributes.operation_factory("DjaggerOptionsAttributes", "options")
DjaggerHeadAttributes = DjaggerAPIAttributes.operation_factory("DjaggerHeadAttributes", "head")

###

DjaggerMethodAttributes = Union[
    DjaggerGetAttributes, 
    DjaggerPostAttributes, 
    DjaggerPatchAttributes, 
    DjaggerPutAttributes, 
    DjaggerDeleteAttributes,
    DjaggerHeadAttributes,
    DjaggerOptionsAttributes
]

# List of all allowable djagger attribute names for a given view
DjaggerViewAttributeList : List[str] = [
    *[ member.value for member in list(DjaggerAPIAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerGetAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerPostAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerPatchAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerDeleteAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerPutAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerOptionsAttributes.__members__.values())],
    *[ member.value for member in list(DjaggerHeadAttributes.__members__.values())],
]

class HttpMethod(str, Enum):
    GET = 'get'
    POST = 'post'
    PATCH = 'patch'
    DELETE = 'delete'
    PUT = 'put'
    OPTIONS = 'options'
    HEAD = 'head'

    @classmethod
    def values(cls):
        """Returns list of http method strings [ 'get', 'post', ... ]"""
        return [ member.value for member in  cls.__members__.values() ]

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
        elif self == self.OPTIONS:
            return DjaggerOptionsAttributes
        elif self == self.HEAD:
            return DjaggerHeadAttributes
        
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