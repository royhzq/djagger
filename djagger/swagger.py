"""
Swagger 2.0 Schema Objects
====================================
"""

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass
from rest_framework import serializers
from typing import Optional, List, Dict, Union, Type
from enum import Enum
from .utils import schema_set_examples, get_url_patterns, extract_unique_schema
from .serializers import SerializerConverter
from .enums import (
    HttpMethod, 
    ViewAttributes,
    DjaggerAttributeEnumType,
    DJAGGER_HTTP_METHODS,
)

import warnings
import inspect
import re
import uuid

class Logo(BaseModel):
    """ Logo image for display on redoc documents. 
    """
    url : Optional[str]
    altText : Optional[str]

class ExternalDocs(BaseModel):
    description: Optional[str]
    url : Optional[str]

class Tag(BaseModel):
    """ OpenAPI `tags` """
    name : str = ""
    description : str = ""
    externalDocs : Optional[ExternalDocs]

class Contact(BaseModel):
    """ OpenAPI `contact` object"""
    name : Optional[str]
    url : Optional[str]
    email : Optional[str]

class License(BaseModel):
    """ OpenAPI `license` object"""
    name : Optional[str]
    url : Optional[str]

class Info(BaseModel):

    """OpenAPI document information"""

    title : str = "Djagger OpenAPI Documentation"
    description : str = Field(" OpenAPI Document Description", description=" OpenAPI descripition")
    termsOfService : str = Field("",description="Reference to any TOS")
    contact : Contact = Field({"email":"example@example.com"}, description="Dict of contact information")
    license : Optional[License]
    version : str = "1.0.5"
    x_logo : Optional[Logo] = Field(alias="x-logo")

    class Config:
        allow_population_by_field_name = True


class TagGroup(BaseModel):
    """ Tag grouping for ``x-tagGroups`` setting in redoc. 
    This beyond the OpenAPI 3.0 specs but is included for redoc.

    Args:
        name (str): Name of Tag grouping.
        tags (List[str]): List of Tag names to include in the grouping.
    """
    name : str 
    tags : List[str] 

class Parameter(BaseModel):
    """ OpenAPI object that includes schema and other details for the particular API endpoint. For POST params """

    name : str
    description : str = ""
    in_: Optional[str] = Field(default="path", alias="in")
    required : Optional[bool] = True #Must be True for GET path parameters
    type_ : Optional[str] = Field(None, alias="type") # POST params do not have this Field
    schema_ : dict = Field(default=None, alias="schema") # Populate with the value of .schema() call on a pydantic model

    class Config:
        allow_population_by_field_name = True


    @classmethod
    def to_parameters(cls, schema : ModelMetaclass, attr : DjaggerAttributeEnumType) -> List['Parameter']:
        """ Converts the fields of a pydantic model to list of Parameter objects for use in generating request parameters.
        All attribute names ending in '_params' are relevant here. Non parameter object attributes should not be passed
        """
        params = []
        if attr == attr.RESPONSE_SCHEMA:
            # response schemas not considered for request parameters
            return params
        
        if "_params" not in attr.value:
            raise AttributeError("`to_parameters` only accepts parameter attributes ending with '_param'")

        if not isinstance(attr, DjaggerAttributeEnumType):
            raise TypeError("attr must be an enum of DjaggerAttributeEnumType type")

        if not isinstance(schema, ModelMetaclass):
            raise TypeError("Parameter object must be pydantic.main.ModelMetaclass type")

        if attr == attr.BODY_PARAMS:
            # Request body handled differently from other parameters
            # Uses #schema in one parameter object
            params = [
                cls(
                    name="body",
                    description=schema.__doc__ if schema.__doc__ else "",
                    in_="body",
                    required=True,
                    type_=None,
                    schema_=extract_unique_schema(schema),
                    model=schema
                )
            ]
            return params
        
        # Handle other parameters - path / query / form / headers/ cookie 
        # with each field as a separate parameter in the list of parameters
        properties = extract_unique_schema(schema).get('properties',{})
        for name, props in properties.items():
            param = cls(
                name=name,
                description=props.get('description', ""),
                in_=attr.location(),
                required=props.get('required', True),
                type_=props.get("type", "")
            )
            params.append(param)
        
        return params


class Response(BaseModel):
        """ OpenAPI Response object for a single http code """
        description: str = ""
        schema_ : dict = Field(default={}, alias="schema") # The value of .schema() call on a pydantic model

        @classmethod
        def _from(cls, model : ModelMetaclass) -> 'Response':
            """ Instantiate Response from a pydantic type model
            """

            if not isinstance(model, ModelMetaclass):
                raise ValueError("Model in response schema must be pydantic.main.ModelMetaclass type")

            return cls(
                description = model.__doc__ if model.__doc__ else "",
                schema=extract_unique_schema(model),
                model=model
            )

        class Config:
            allow_population_by_field_name = True


class EndPoint(BaseModel):
    """OpenAPI object for a given http method under a SwaggerPath"""

    tags : List[str] = []
    summary : str = ""
    description : str = ""
    operationId : Optional[str]
    consumes : List[str] = ["application/json"]
    produces : List[str] = ["application/json"]
    parameters : List[Parameter] = []
    responses: Dict[str, Response] = {}

    def _extract_consumes(self, view : Type, http_method: HttpMethod):

        """`consumes` attribute is initialized on the end point in the following priority:
        1. Look for `consumes` the http method level e.g., `get_consumes`, `post_consumes` attribute
        2. If not, look for `consumes` set at the api level e.g. `consumes` attribute (which would apply to all http methods unless 1. exists)
        """

        consumes = ViewAttributes.from_view(view, "consumes", http_method)
        if consumes:
            assert isinstance(consumes, List), "consumes attribute must be a list"
            self.consumes = consumes


    def _extract_produces(self, view : Type, http_method: HttpMethod):

        """`produces` attribute is initialized on the end point in the following priority:
        1. Look for `produces` the http method level e.g., `get_produces`, `post_produces` attribute
        2. If not, look for `produces` set at the api level e.g. `produces` attribute (which would apply to all http methods unless 1. exists)
        """

        produces = ViewAttributes.from_view(view, "produces", http_method)
        if produces:
            assert isinstance(produces, List), "produces attribute must be a list"
            self.produces = produces

    def _extract_summary(self, view : Type, http_method: HttpMethod):
        """`summary` attribute is initialized on the end point in the following priority:
        1. Look for `summary` the http method level e.g., `get_summary`, `post_summar` attribute
        2. If not, look for `summary` set at the api level e.g. `summary` attribute (which would apply to all http methods unless 1. exists)
        3. If not, set `summary` to be the API class name.
        """

        summary = ViewAttributes.from_view(view, 'summary', http_method)

        if not summary:
            summary = view.__name__     

        if summary:
            assert isinstance(summary, str), "summary must be string type"
            self.summary = summary

    def _extract_description(self, view : Type, http_method: HttpMethod):
        """`description` attribute is initialized on the end point in the following priority:
        1. Look for `description` the http method level e.g., `get_description`, `post_description` attribute
        2. If not, look for `description` set at the api level e.g. `description` attribute (which would apply to all http methods unless 1. exists)
        3. If not, set `description` to be the docstrings in the view.
        """

        description = ViewAttributes.from_view(view, 'description', http_method)

        if not description:
            description = view.__doc__   

        assert isinstance(description, (str, type(None))), "description must be string type"
        self.description = description

    def _extract_tags(self, view : Type, http_method: HttpMethod):
        """ `tags` attribute is initialized on the end point in the following priority:
        1. Look for tags set at the http method level e.g., `get_tags`, `post_tags` attribute
        2. If not, look for tags set at the api level e.g. `tags` attribute (which would apply to all http methods unless 1. exists)
        3. If not, set the tags to be default as the app module name in which the api resides in.
        """

        tags = ViewAttributes.from_view(view, 'tags', http_method)

        if not tags:
            tags = [view.__module__.split(".")[0]] # Set tags as the app module name of the API as fallback

        if tags:
            assert isinstance(tags, List), "tags attribute must be a list of strings"
            self.tags = tags

    def _extract_parameters(self, view : Type, http_method: HttpMethod):
        """ Helper to initialize request `parameters` from a View for a given http method
        """

        self.parameters = []

        for attr in ViewAttributes.api.__members__.values():
            
            if "_params" not in attr:
                # only consider relevant for parameter attributes - attr name ending in '_params'
                continue

            request_schema = ViewAttributes.from_view(view, attr.value, http_method)
            if not request_schema:
                continue

            # Converting serializers to pydantic models
            if isinstance(request_schema, serializers.SerializerMetaclass):
                request_schema = SerializerConverter(s=request_schema()).to_model()

            self.parameters += Parameter.to_parameters(request_schema, attr)


    def _extract_responses(self, view : Type, http_method : HttpMethod):
        """ Helper to initialize `responses` from a view class and returns responses dict for EndPoint
        """
        if not isinstance(http_method, HttpMethod):
            raise TypeError("http_method is not a valid HttpMethod type")

        responses = {}

        response_schema = ViewAttributes.from_view(view, 'response_schema', http_method)

        # When attribute is a pydantic model - assume 200 response only
        if isinstance(response_schema, ModelMetaclass):
            responses = { 
                '200': Response._from(response_schema)
            }
        # When attribute is a Serializer - assume 200 response only
        elif isinstance(response_schema, serializers.SerializerMetaclass):
            responses = {
                '200': Response._from(SerializerConverter(s=response_schema()).to_model())
            }
        # When attribute is a dict of responses, prepare dict of Response values
        elif isinstance(response_schema, Dict):
            for status_code, model in response_schema.items():
                if not isinstance(status_code, str):
                    raise ValueError("key in response schema dict needs to be string")

                # Converting serializers to pydantic models
                if isinstance(model, serializers.SerializerMetaclass):
                    model = SerializerConverter(s=model()).to_model()

                responses[status_code] = Response._from(model)


        
        self.responses = responses
        

    @classmethod
    def _from(cls, view : Type, http_method : HttpMethod) -> Union['EndPoint', None]:
        """ Extract attributes from a view class to instantiate EndPoint given the type of http method for the endpoint.
        Wil return None if exclude attribute is True.
        """
        
        endpoint = cls(
            tags = [],
            summary = "",
            description = "",
            parameters = [],
            responses = {}
        )

        # Exclude at the method-level if `<http_method>_djagger_exclude` is True
        exclude = ViewAttributes.from_view(view, 'djagger_exclude', http_method)
        if exclude:
            return None

        endpoint._extract_tags(view, http_method)
        endpoint._extract_summary(view, http_method)
        endpoint._extract_consumes(view, http_method)
        endpoint._extract_produces(view, http_method)
        endpoint._extract_description(view, http_method)
        endpoint._extract_parameters(view, http_method)
        endpoint._extract_responses(view, http_method)

        return endpoint

class Path(BaseModel):
    """ OpenAPI Path Object """
    post : Optional[EndPoint]
    get : Optional[EndPoint]
    put : Optional[EndPoint]
    patch : Optional[EndPoint]
    delete : Optional[EndPoint]
    options : Optional[EndPoint]
    head : Optional[EndPoint]

    @classmethod
    def create(cls, view : Type) -> 'Path':
        """ Given a Class-based view or a function based view, create the Path object 
        from the Djagger attributes set in the view.
        """
        path = cls()
        
        if inspect.isclass(view):
            # For CBV or DRF API, check for methods by looking for get(), post(), patch(), put(), delete() methods
            for http_method in HttpMethod.__members__.values():
                if hasattr(view, http_method):
                    if callable(getattr(view, http_method)):
                        endpoint = EndPoint._from(view, http_method)
                        if not endpoint:
                            continue
                        if not endpoint.responses:
                            continue

                        setattr(path, http_method, endpoint)

        elif inspect.isfunction(view):

            # Handle DRF ViewSets 
            # DRF ViewSets are function based views with an ``actions`` attr which is a dict
            # of http_methods as keys. 

            # TODO: Handle each ViewSet function with separate schemas, treating each function
            # `retrieve`, `list` etc. as one FBV each
            
            if hasattr(view, 'actions'):
                for k in view.actions.keys():
                    try:
                        http_method = HttpMethod(k)
                    except ValueError:
                        continue

                    endpoint = EndPoint._from(view, http_method)
                    if not endpoint:
                        continue
                    if not endpoint.responses:
                        continue
                    setattr(path, http_method, endpoint)

            # For FBVs, check for existence of http methods from the `djagger_http_methods` attribute
            # set by the @schema decorator

            if not hasattr(view, DJAGGER_HTTP_METHODS):
                return path

            for method in getattr(view, DJAGGER_HTTP_METHODS, []):
                http_method = HttpMethod(method.lower())
                endpoint = EndPoint._from(view, http_method)
                if not endpoint:
                    continue
                if not endpoint.responses:
                    continue
                setattr(path, http_method, endpoint)

        return path

class Document(BaseModel):
    
    """
    OpenAPI base document

    Args:
        swagger (str) : Swagger version number.
        info (Info) : ``Info`` object.
        host (str): Hostname for APIs.
        basePath (str): Base path of URL e.g., ``/V1``.
        tags (List[Tag]) : List of ``Tag`` objects.
        schemes (List[str]) : List of URL schemes. Defaults to ``['http', 'https']``.
        paths (Dict[str, Path]): Dictionary containing route as the key and ``Path`` object as its value.
        securityDefinitions (Dict): WIP
        definitions (Dict[str, dict]): Dictionary containing OpenAPI definitions.
        x_tag_groups (List[TagGroup]) : List of ``TagGroup`` tag groupings if any.
    """ 

    swagger : str = "2.0"
    info : Info
    host : str = ""
    basePath : str = ""
    tags : List[Tag] = []
    schemes : List[str] = Field(["https", "http"])
    paths : Dict[str, Path] = {}
    securityDefinitions : dict = {} # Incomplete
    definitions : Dict[str, dict] = {}
    x_tag_groups : Optional[List[TagGroup]] = Field(alias="x-tagGroups")

    class Config:
        allow_population_by_field_name = True


    def compile_definitions(self):
        """ Build up definitions at the base document by compiling all pydantic models in parameters and responses . 
        Also deletes individual definitions field for the schemas in parameters and responses.
        """
        definitions = {}
        for path in self.paths.values():
            for http_method in HttpMethod.values():
                endpoint = getattr(path, http_method)
                if not endpoint:
                    continue

                for response in endpoint.responses.values():
                    if hasattr(response ,"schema_"):
                        if isinstance(response.schema_, Dict):
                            if response.schema_.get('definitions'):
                                definitions.update(response.schema_.pop('definitions'))

                for parameter in endpoint.parameters:
                    if hasattr(parameter ,"schema_"):
                        if isinstance(parameter.schema_, Dict):
                            if parameter.schema_.get('definitions'):
                                definitions.update(parameter.schema_.pop('definitions'))

        self.definitions = definitions
        return 

    @classmethod
    def generate(
        cls,
        app_names : List[str] = [],
        tags : List[Tag] = [],
        swagger = "2.0",
        host = "example.org",
        basePath = "",
        description = "",
        schemes = ['https', 'http'],
        version = "1.0.5",
        title = "Djagger OpenAPI Documentation",
        terms_of_service = "",
        contact_name = None,
        contact_email = "",
        contact_url = "",
        license_name = "",
        license_url = "",
        x_tag_groups : List[TagGroup]= []
    ) -> dict :
        """ Inspects URLPatterns in given list of apps to generate the openAPI json object for the Django project.
        Returns the JSON string object for the resulting OAS document.
        """
        
        url_patterns = get_url_patterns(app_names)
        paths : Dict[str, Path] = {}

        for route, url_pattern in url_patterns:

            try:
                view = url_pattern.callback.view_class # Class-based View
            except AttributeError:
                view = url_pattern.callback # Function-based View / ViewSet 
            
            exclude = ViewAttributes.from_view(view, 'djagger_exclude', None)
            if exclude:
                continue
            
            path = Path.create(view)

            # If path has none of the methods documented, skip its documentation
            if getattr(path, 'get', None) or \
                getattr(path, 'post', None) or \
                getattr(path, 'put', None) or \
                getattr(path, 'patch', None) or \
                getattr(path, 'delete', None):

                    paths["/" + route] = path
        
        # Create tag objects as provided
        # Note that if tags supplied is empty, they will still be generated when
        # set as attributes in the individual API or endpoints
        tags = [
            Tag(name=tag["name"], description=tag.get("description","")) for tag in tags
        ]
        info = Info(
            description=description,
            version=version,
            title=title,
            termsOfService=terms_of_service,
            contact=Contact(
                name=contact_name,
                email=contact_email,
                url=contact_url
            ),
            license=License(
                name=license_name,
                url=license_url
            ),
        )
        document = cls(
            swagger=swagger,
            host=host,
            info=info,
            basePath=basePath,
            schemes=schemes,
            tags=tags,
            paths=paths,
            x_tag_groups=x_tag_groups,
        )
        document.compile_definitions()

        return document.dict(by_alias=True, exclude_none=True)


