# Types for OpenAPI swagger document

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.main import ModelMetaclass # Abstract classes derived from BaseModel
from typing import Optional, List, Dict, Union, Type
from enum import Enum
from .utils import base_model_set_examples, get_url_patterns
from .enums import (
    HttpMethod, 
    ParameterLocation, 
    DjaggerAPIAttributes,
    DjaggerMethodAttributes,
    DjaggerGetAttributes, 
    DjaggerPostAttributes, 
    DjaggerPatchAttributes, 
    DjaggerPutAttributes, 
    DjaggerDeleteAttributes,
    DJAGGER_HTTP_METHODS,
)

from collections import Counter
import warnings
import inspect
import re

class DjaggerInfo(BaseModel):

    """OpenAPI document information"""

    description : str = Field("Djagger OpenAPI Document Description", description="Djagger OpenAPI descripition")
    version : str = "1.0.5"
    title : str = "Djagger OpenAPI Documentation"
    termsOfService : str = Field("",description="Reference to any TOS")
    contact : Dict[str, str] = Field({"email":"example@example.com"}, description="Dict of contact information")
    license : Dict[str, str] = {
        "name": "Apache 2.0",
        "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
    }

class DjaggerExternalDocs(BaseModel):
    description: str
    url : str

class DjaggerTag(BaseModel):
    """ OpenAPI `tags` """
    name : str = ""
    description : str = ""
    externalDocs : Optional[DjaggerExternalDocs]

class DjaggerParameter(BaseModel):
    """ OpenAPI object that includes schema and other details for the particular API endpoint. For POST params """
    # Use .json(by_alias=True) to get json with alias field names
    name : str
    description : str = ""
    in_: Optional[str] = Field(default="path", alias="in") # 'in' is a reserved keyword in python
    required : Optional[bool] = True #Optional for response parameters. Must be True for GET pathe parameters
    type_ : Optional[str] = Field(None, alias="type") # POST params cannot have this Field
    schema_ : dict = Field(default=None, alias="schema") # The value of .schema() call on a pydantic model

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def to_parameters(cls, schema : ModelMetaclass, attr : DjaggerMethodAttributes) -> List['DjaggerParameter']:
        """ Converts the fields of a pydantic model to list of DjaggerParameter objects for use in generating request parameters.
        All attribute names ending in '_params' are relevant here. Non parameter object attributes should not be passed
        """
        params = []
        if not isinstance(attr, DjaggerMethodAttributes.__args__):
            raise TypeError("DjaggerParameter.to_parameters requires attr to be of type `DjaggerMethodAttributes`")

        if attr == attr.RESPONSE_SCHEMA:
            # response schemas not considered for request parameters
            return params
        
        if "_params" not in attr.value:
            raise AttributeError("`to_parameters` only accepts parameter attributes ending with '_param'")

        if not isinstance(schema, ModelMetaclass):
            raise TypeError("Parameter object must be pydantic.main.ModelMetaclass type")

        base_model_set_examples(schema)

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
                    schema_=schema.schema()
                )
            ]
            return params
        
        # Handle other parameters - path / query / form / headers/ cookie 
        # with each field as a separate parameter in the list of parameters
        properties = schema.schema().get('properties',{})
        for name, props in properties.items():
            param = cls(
                name=name,
                description=props.get('description', ""),
                in_=ParameterLocation.from_method_attribute(attr).value,
                required=props.get('required', True),
                type_=props.get("type", "")
            )
            params.append(param)
        
        return params


class DjaggerResponse(BaseModel):
        """ OpenAPI Response object for a single http code """
        description: str = ""
        schema_ : dict = Field(default={}, alias="schema") # The value of .schema() call on a pydantic model

        @classmethod
        def _from(cls, model : ModelMetaclass) -> 'DjaggerResponse':
            """ Instantiate DjaggerResponse from a pydantic type model
            """
            base_model_set_examples(model)
            return cls(
                description = model.__doc__ if model.__doc__ else "",
                schema=model.schema()
            )

        class Config:
            allow_population_by_field_name = True


class DjaggerEndPoint(BaseModel):
    """OpenAPI object for a given http method under a SwaggerPath"""

    tags : List[str] = []
    summary : str = ""
    description : str = ""
    operationId : Optional[str]
    consumes : List[str] = ["application/json"]
    produces : List[str] = ["application/json"]
    parameters : List[DjaggerParameter] = []
    responses: Dict[str, DjaggerResponse] = {}

    def _extract_consumes(self, view : Type, http_method: HttpMethod):
        #TODO: Initialize `consumes` field
        return None

    def _extract_produces(self, view : Type, http_method: HttpMethod):
        #TODO: Initialize `produces` field
        return None

    def _extract_summary(self, view : Type, http_method: HttpMethod):
        """`summary` attribute is initialized on the end point in the following priority:
        1. Look for `summary` the http method level e.g., `get_summary`, `post_summart` attribute
        2. If not, look for `summary` set at the api level e.g. `summary` attribute (which would apply to all http methods unless 1. exists)
        3. If not, set `summary` to be the API class name.
        """

        # 1. Get summary specific to endpoint http method
        djagger_method_attributes = http_method.to_djagger_attribute()
        try:
            summary = getattr(view, djagger_method_attributes.SUMMARY.value)
            if not isinstance(summary, str):
                raise TypeError('summary attribute must be string')
            self.summary = summary
            return
        except AttributeError:
            pass

        # 2. Get summary at the API level
        try:
            summary = getattr(view, DjaggerAPIAttributes.SUMMARY.value)
            if not isinstance(summary, str):
                raise TypeError('summary attribute must be string')
            self.summary = summary
            return
        except AttributeError:
            pass

        # 3. Get summary as the API Name
        self.summary = view.__name__
        return

    def _extract_description(self, view : Type, http_method: HttpMethod):
        """`description` attribute is initialized on the end point in the following priority:
        1. Look for `description` the http method level e.g., `get_description`, `post_description` attribute
        2. If not, look for `description` set at the api level e.g. `description` attribute (which would apply to all http methods unless 1. exists)
        3. If not, set `description` to be the docstrings in the view.
        """

        # 1. Get description specific to endpoint http method
        djagger_method_attributes = http_method.to_djagger_attribute()
        try:
            description = getattr(view, djagger_method_attributes.DESCRIPTION.value)
            if not isinstance(description, str):
                raise TypeError('description attribute must be string')
            self.description = description
            return
        except AttributeError:
            pass

        # 2. Get description at the API level
        try:
            description = getattr(view, DjaggerAPIAttributes.DESCRIPTION.value)
            if not isinstance(description, str):
                raise TypeError('description attribute must be string')
            self.description = description
            return
        except AttributeError:
            pass

        # 3. Get description as the API docstring
        self.description = view.__doc__ if view.__doc__ else ""
        return

    def _extract_tags(self, view : Type, http_method: HttpMethod):
        """ `tags` attribute is initialized on the end point in the following priority:
        1. Look for tags set at the http method level e.g., `get_tags`, `post_tags` attribute
        2. If not, look for tags set at the api level e.g. `tags` attribute (which would apply to all http methods unless 1. exists)
        3. If not, set the tags to be default as the app module name in which the api resides in.
        """

        # 1. Get tags specific to endpoint http method
        djagger_method_attributes = http_method.to_djagger_attribute()
        try:
            tags = getattr(view, djagger_method_attributes.TAGS.value)
            if not isinstance(tags, List):
                raise TypeError('tags attribute must be a list of strings')
            self.tags = tags
            return

        except AttributeError:
            pass

        # 2. Get tags at the API level
        try:
            tags = getattr(view, DjaggerAPIAttributes.TAGS.value)
            if not isinstance(tags, List):
                raise TypeError('tags attribute must be a list of strings')
            self.tags = tags
            return
        except AttributeError:
            pass

        # 3. Set tags as the app module name of the API
        tags = [view.__module__.split(".")[0]]

        self.tags = tags
        return

    def _extract_parameters(self, view : Type, http_method: HttpMethod):
        """ Helper to initialize request `parameters` from a View for a given http method
        """

        self.parameters = []
        djagger_method_attributes : DjaggerMethodAttributes = http_method.to_djagger_attribute()

        for attr in djagger_method_attributes.__members__.values():
            if not hasattr(view, attr.value):
                # skip if View does not contain attribute
                continue            
            if "_params" not in attr.value:
                # only relevant for parameter attributes - attr name ending in '_params'
                continue
            request_schema = getattr(view, attr.value)

            self.parameters += DjaggerParameter.to_parameters(request_schema, attr)

        return

    def _extract_responses(self, view : Type, http_method : HttpMethod):
        """ Helper to initialize `responses` from a view class and returns responses dict for DjaggerEndPoint
        """
        if not isinstance(http_method, HttpMethod):
            raise TypeError("http_method is not a valid HttpMethod type")

        responses = {}

        schema_attr : DjaggerMethodAttributes = http_method.to_djagger_attribute().RESPONSE_SCHEMA
        response_schema = getattr(view, schema_attr.value, None)

        # When attribute is a pydantic model - assume 200 response only
        if isinstance(response_schema, ModelMetaclass):
            responses = { 
                '200': DjaggerResponse._from(response_schema)
            }
        elif isinstance(response_schema, Dict):
            # When attribute is a dict of responses, prepare dict of DjaggerResponse values
            for status_code, model in response_schema.items():
                if not isinstance(status_code, str):
                    raise ValueError("key in response schema dict needs to be string")
                if not isinstance(model, ModelMetaclass):
                    raise ValueError("Model in response schema must be pydantic.main.ModelMetaclass type")

                responses[status_code] = DjaggerResponse._from(model)
        
        self.responses = responses
        

    @classmethod
    def _from(cls, view : Type, http_method : HttpMethod) -> 'DjaggerEndPoint':
        """ Extract attributes from a view class to instantiate DjaggerEndPoint given the type of http method for the endpoint
        """
        
        endpoint = cls(
            tags = [],
            summary = "",
            description = "",
            parameters = [],
            responses = {}
        ) 

        endpoint._extract_tags(view, http_method)
        endpoint._extract_summary(view, http_method)
        endpoint._extract_description(view, http_method)
        endpoint._extract_parameters(view, http_method)
        endpoint._extract_responses(view, http_method)

        return endpoint

class DjaggerPath(BaseModel):
    """ OpenAPI Path Object """
    post : Optional[DjaggerEndPoint]
    get : Optional[DjaggerEndPoint]
    put : Optional[DjaggerEndPoint]
    patch : Optional[DjaggerEndPoint]
    delete : Optional[DjaggerEndPoint]

    @classmethod
    def create(cls, view : Type) -> 'DjaggerPath':
        """ Given a Class-based view or a function based view, create the DjaggerPath object 
        from the Djagger attributes set in the view.
        """
        path = cls()
        
        if inspect.isclass(view):
            # For CBV or DRF API, check for methods by looking for get(), post(), patch(), put(), delete() methods
            for http_method in HttpMethod.__members__.values():
                if hasattr(view, http_method):
                    if callable(getattr(view, http_method)):
                        setattr(path, http_method.value, DjaggerEndPoint._from(view, http_method))

        elif inspect.isfunction(view):
            # For FBVs, check for existence of http methods from the `djagger_http_methods` attribute
            # set by the @schema decorator

            if not hasattr(view, DJAGGER_HTTP_METHODS):
                return path

            for method in getattr(view, DJAGGER_HTTP_METHODS, []):
                http_method = HttpMethod(method.lower())
                setattr(path, http_method.value, DjaggerEndPoint._from(view, http_method))

        return path

class DjaggerDoc(BaseModel):
    
    """OpenAPI base document"""

    swagger : str = "2.0"
    info : DjaggerInfo = DjaggerInfo()
    host : str = ""
    basePath : str = ""
    tags : List[DjaggerTag] = []
    schemes : List[str] = Field(["https", "http"])
    paths : Dict[str, DjaggerPath] = {}
    securityDefinitions : dict = {} # Incomplete
    definitions : Dict[str, dict] = {}

    @staticmethod
    def clean_route(route : str) -> str:
        """ Converts a django path route string format into an openAPI route format.
        Example:
            Django format: '/list/<int:pk>' 
                to
            OpenAPI format: '/list/{pk}'
        """
        return re.sub(r'<[a-zA-Z0-9\-\_]*:([a-zA-Z0-9\-\_]*)>', r'{\1}', route)


    @classmethod
    def generate_openapi(
        cls,
        app_names : List[str] = [],
        tags : List[DjaggerTag] = [],
        swagger = "2.0",
        host = "example.org",
        basePath = "",
        description = "",
        schemes = ['https', 'http'],
        version = "1.0.5",
        title = "Djagger OpenAPI Documentation",
        terms_of_service = "",
        contact_name = "",
        contact_email = "",
        contact_url = "",
        license_name = "",
        license_url = ""
    ) -> dict :
        """ Inspects URLPatterns in given list of apps to generate the openAPI json object for the Django project.
        Returns the JSON string object for the resulting OAS document.
        """
        
        url_patterns = get_url_patterns(app_names)
        paths : Dict[str, DjaggerPath] = {}

        for url_pattern in url_patterns:
            # Either `path()` or `re_path()` are valid
            # `re_path()` does not have _route attribute
            if hasattr(url_pattern.pattern, '_route'):
                route = "/" + url_pattern.pattern._route
            elif hasattr(url_pattern.pattern, 'regex'):
                route = "/" + url_pattern.pattern.regex.pattern.replace("^", "").replace("$", "")
                warnings.warn("Warning: re_path is not recommended. Please use path() for url patterns if possible.")
            else:
                raise AttributeError("urlpattern does not contain _route or regex. Make sure you are using path() in your url patterns")

            route = DjaggerDoc.clean_route(route)

            try:
                view = url_pattern.callback.view_class # Class-based View
            except AttributeError:
                view = url_pattern.callback # Function-based View
            
            if hasattr(view, DjaggerAPIAttributes.DJAGGER_EXCLUDE.value):
                # Exclude generating docs for views with `djagger_exclude=True`
                if view.djagger_exclude:
                    continue
            
            paths[route] = DjaggerPath.create(view)

        # Create tag objects as provided
        # Note that if tags supplied is empty, they will still be generated when
        # set as attributes in the individual API or endpoints
        tags = [
            DjaggerTag(name=tag["name"], description=tag.get("description","")) for tag in tags
        ]
        info = DjaggerInfo(
            description=description,
            version=version,
            title=title,
            termsOfService=terms_of_service,
            contact={
                "name":contact_name,
                "email":contact_email,
                "url":contact_url
            },
            license={
                "name":license_name,
                "url":license_url
            },
        )
        document = cls(
            swagger=swagger,
            host=host,
            info=info,
            basePath=basePath,
            schemes=schemes,
            tags=tags,
            paths=paths,
        )

        return document.dict(by_alias=True, exclude_none=True)


