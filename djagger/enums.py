"""
Enums
=====
"""
from typing import Union, List, Any, Type, Callable
from enum import Enum

DJAGGER_HTTP_METHODS = (
    "djagger_http_methods"  # FBV attribute name for http methods used in the FBV
)


class HttpMethod(str, Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"
    PUT = "put"
    OPTIONS = "options"
    HEAD = "head"
    TRACE = "trace"

    @classmethod
    def values(cls):
        """Returns list of http method strings [ 'get', 'post', ... ]"""
        return [member.value for member in cls.__members__.values()]


class DjaggerAttributeEnumType(str, Enum):

    """Enum type with helper class methods to initialize View-level and operation-level djagger view attributes as enums"""

    @classmethod
    def items(cls):
        """ List of tuples of the enum attr names and the corresponding value"""
        return [(k, v.value) for k, v in cls.__members__.items()]

    @classmethod
    def values(cls):
        """ List of enum attr string values"""
        return [m.value for m in cls.__members__.values()]

    def location(self) -> Union[str, type(None)]:
        """Returns the 'in' location value for parameters"""
        location_map = {
            "PATH_PARAMS": "path",
            "QUERY_PARAMS": "query",
            "HEADER_PARAMS": "header",
            "COOKIE_PARAMS": "cookie",
            "BODY_PARAMS": "body",
        }

        return location_map.get(self.name, None)


class DjaggerViewAttributes:
    """Contains enums for djagger attributes that can be extracted from a view class of function"""

    # Mapping of enums to djagger attrs that may be found in a view
    view_attrs = {
        "PATH_PARAMS": "path_params",
        "QUERY_PARAMS": "query_params",
        "HEADER_PARAMS": "header_params",
        "COOKIE_PARAMS": "cookie_params",
        "BODY_PARAMS": "body_params",
        "RESPONSE_SCHEMA": "response_schema",
        "SUMMARY": "summary",
        "TAGS": "tags",
        "DESCRIPTION": "description",
        "CONSUMES": "consumes",  # swagger 2.0
        "PRODUCES": "produces",  # swagger 2.0
        "OPERATION_ID": "operation_id",
        "DEPRECATED": "deprecated",
        "EXTERNAL_DOCS": "external_docs",
        "SERVERS": "servers",
        "SECURITY": "security",
        "DJAGGER_EXCLUDE": "djagger_exclude",
    }

    def retrieve_operation_attr_value(self, attr: str, http_method: HttpMethod) -> str:
        """Converts an API-level attribute value to the operation-level equivalent given a string attribute value ``attr`` and a given http method.

        Example::

            >>> self.retrieve_operation_attr_value('summary', HttMethod.GET)
            'get_summary'
        """

        attr_name = self.api(attr).name
        operation_attr_enum = getattr(self, http_method.value)
        operation_attr_value = getattr(operation_attr_enum, attr_name)

        return operation_attr_value

    def from_view(
        self,
        view: Union[Type, Callable],
        attr: str,
        http_method: Union[HttpMethod, type(None)] = None,
    ) -> Any:

        """Given a FBV view or CBV view, the general attribute name, and a http method, extracts the attribute from the view starting at the operation-level attribute i.e. get_body_params.
        If it does not exist, try to extract at the API-level attribute i.e. body_params.
        If the attribute still does not exist, return None.
        If http_method is not passed, only extract the API-level attribute.

        Example::
            >>> ViewAttrs = DjaggerViewAttributes("get")
            >>> ViewAttrs.from_view(view, 'operation_id', HttpMethod.GET)
            "get_operation_id"

        """

        value = None

        if http_method:
            operation_attr_value = self.retrieve_operation_attr_value(attr, http_method)
            value = getattr(view, operation_attr_value, getattr(view, attr, None))
        else:
            value = getattr(view, attr, None)

        # If failed to extract any value from FBV, look for parent class and attempt to extract
        # from parent class 'cls' attributes if parent class exists

        if value == None and hasattr(view, "cls"):
            return self.from_view(view.cls, attr=attr, http_method=http_method)

        return value

    def operation(self, http_method: HttpMethod) -> DjaggerAttributeEnumType:
        """ Returns the DjaggerAttributeEnumType value for the corresponding HttpMethod"""
        op = getattr(self, http_method.value, None)
        if not op:
            raise AttributeError(
                f"Http method {http_method.value} not found as a callable method in {self.__name__}"
            )
        return op

    @classmethod
    def prefix_attrs(cls, method_prefix: str, custom_prefix: str = ""):
        """Prefixes view_attrs values with string prefix e.g. ``get_`` in 'get_operation_id'"""
        return {
            k: f"{custom_prefix}{method_prefix}_{v}" for k, v in cls.view_attrs.items()
        }

    def __init__(self, custom_prefix: str, *http_methods):

        # Handle custom view_attrs for case where custom_prefix provided
        view_attrs = {k: f"{custom_prefix}{v}" for k, v in self.view_attrs.items()}

        self.custom_prefix = custom_prefix
        self.http_methods = http_methods
        self.api = DjaggerAttributeEnumType(
            "api", view_attrs
        )  # API-level attribute Enum e.g. 'body_params'
        self.attr_list = self.api.values()

        for http_method in http_methods:
            # Create operation-level attribute Enum for each operation e.g. 'get_body_params'
            setattr(
                self,
                http_method,
                DjaggerAttributeEnumType(
                    http_method,
                    self.prefix_attrs(
                        method_prefix=http_method, custom_prefix=self.custom_prefix
                    ),
                ),
            )
            self.attr_list += getattr(self, http_method).values()


ViewAttributes = DjaggerViewAttributes("", *HttpMethod.values())
