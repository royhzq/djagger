"""
OpenAPI 3.0 Schema Objects
====================================
"""

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass
from typing import Optional, List, Dict, Union, Type, Any
from .utils import base_model_set_examples, get_url_patterns

from .enums import (
    HttpMethod, 
    ParameterLocation, 
    DjaggerAPIAttributes,
    DjaggerMethodAttributes,
    DJAGGER_HTTP_METHODS,
)

import uuid
import inspect
import warnings

class Logo(BaseModel):
    """ Logo image for display on redoc documents. 
    """
    url : Optional[str]
    altText : Optional[str]

class ExternalDocs(BaseModel):
    description: Optional[str]
    url : str

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

    title : str = "Djagger OpenAPI 3.0 Documentation"
    description : str = " OpenAPI 3.0 Document Description"
    termsOfService : str = ""
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


class ServerVariable(BaseModel):

    enum : Optional[List[str]] 
    default : str
    description : str

class Server(BaseModel):
    """ Server object in OpenAPI 3.0
    """
    url : str
    description : str = "'"
    variables : Optional[Dict[str, ServerVariable]]

class Reference(BaseModel):

    # Use method .dict(by_alias=True)

    ref : str = Field(alias="$ref")

    class Config:
        allow_population_by_field_name = True

class Example(BaseModel):
    summary : str = ""
    description : str = ""
    value : Any
    externalValue : Optional[str]


class OAuthFlow(BaseModel):
    authorizationUrl : str
    tokenURL : str
    refreshURL : Optional[str]
    scopes : Dict[str, str]


class OAuthFlows(BaseModel):
    implicit : Optional[OAuthFlow]
    password : Optional[OAuthFlow]
    clientCredentials : Optional[OAuthFlow]
    authorizationCode : Optional[OAuthFlow]


SecurityRequirement = Dict[str, List[str]]


class SecurityScheme(BaseModel):
    
    type_ : str = Field(alias="type")
    desccription : str = ""
    name : str
    in_ : str = Field(alias="in")
    scheme : str 
    bearerFormat : Optional[str]
    flows : OAuthFlows 
    openIdConnectUrl : str

class Header(BaseModel):
    """ The Header Object follows the structure of the Parameter Object with the following changes:
    1. ``name`` MUST NOT be specified, it is given in the corresponding headers map.
    2. ``in`` MUST NOT be specified, it is implicitly in header.
    3. All traits that are affected by the location MUST be applicable to a location of header (for example, style).
    """
    description : str = ""
    required : bool = False
    deprecated : bool = False
    allowEmptyValue : bool = False
    style : Optional[str]
    explode : bool = False
    allowReserved : bool = False
    schema_ : Optional[Union[Dict, Reference]] = Field(alias="schema") # schema can take in a `.schema()` dict value from pydantic
    example : Optional[Any]
    examples : Optional[Dict[str, Union[Example, Reference]]]

    class Config:
        allow_population_by_field_name = True

class Encoding(BaseModel):
    contentType : str
    headers : Dict[str, Union[Header, Reference]]
    style : Optional[str]
    explode : bool = False
    allowReserved : bool = False    

class MediaType(BaseModel):
    schema_ : Optional[Union[Dict, Reference]] = Field(alias="schema") # schema can take in a `.schema()` dict value from pydantic
    example : Optional[Any]
    examples : Optional[Dict[str, Union[Example, Reference]]]
    encoding : Optional[Dict[str, Encoding]]

    class Config:
        allow_population_by_field_name = True
    
    @classmethod
    def _from(cls, model : ModelMetaclass, component : str = "schemas") -> 'MediaType':
        """Generates an instance of MediaType from a pydantic model"""
        
        media = cls()

        base_model_set_examples(model)
        media.schema_ = Components.extract_component_schema(model, component)
        
        # Generate example
        if hasattr(model, 'example'):
            if callable(model.example):
                media.example = model.example()

        # TODO: Handle multiple examples for ``examples`` field
        
        # Look for ``encoding`` in model Config and instantiate it 
        encoding = getattr(model.Config, 'encoding', {})

        if not isinstance(encoding, Dict):
            raise TypeError('encoding in model Config needs to be a Dict')

        if encoding:
            # TODO: validation for internals of ``encoding``
            media.encoding = encoding

        return media

class Parameter(BaseModel):
    name : str
    in_ : str = Field(alias="in")
    description : str = ""
    required : bool = False
    deprecated : bool = False
    allowEmptyValue : bool = False
    style : Optional[str]
    explode : bool = False
    allowReserved : bool = False
    schema_ : Optional[Union[Dict, Reference]] = Field(alias="schema") # schema can take in a `.schema()` dict value from pydantic
    example : Optional[Any]
    examples : Optional[Dict[str, Union[Example, Reference]]]
    content : Optional[Dict[str, MediaType]] # For more complex values - unused for now.

    class Config:
        allow_population_by_field_name = True

class RequestBody(BaseModel):
    description : Optional[str]
    content : Dict[str, MediaType] = {}
    required : bool = False

class Response(BaseModel):
    description : str = ""
    headers : Optional[Dict[str, Union[Header, Reference]]]
    content : Optional[Dict[str, MediaType]]
    # links : Optional[Dict] # Not supported yet

class Operation(BaseModel):
    
    tags : List[str] = []
    summary : str = ""
    description : str = ""
    externalDocs : Optional[ExternalDocs]
    operationId : Optional[str]
    parameters : List[Union[Parameter, Reference]] = []
    requestBody : Optional[Union[RequestBody, Reference]]
    responses: Dict[str, Response] = {} # Keys can be 'default' or http method '200', etc
    # callbacks : Optional[Dict[str, Dict[str, Union[Path, Reference]]]] # Circular reference with Path
    deprecated : bool = False
    security : Optional[SecurityRequirement]
    servers : Optional[List[Server]]

    def _extract_operationId(self, view : Type, http_method: HttpMethod):
        ...
        return

    def _extract_externalDocs(self, view : Type, http_method: HttpMethod):
        ...
        return

    def _extract_parameters(self, view : Type, http_method: HttpMethod):
        ...
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


    def _extract_summary(self, view : Type, http_method: HttpMethod):
        """`summary` attribute is initialized on the end point in the following priority:
        1. Look for `summary` the http method level e.g., `get_summary`, `post_summary` attribute
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

    def _extract_parameters(self, view : Type, http_method: HttpMethod):
        ...
        return

    def _extract_request_body(self, view : Type, http_method: HttpMethod):
        """ Extracts ``requestBody`` from the ``<http_method>_BODY_PARAMS`` attribute from the view.
        ``<http_method>_BODY_PARAMS`` value can be of the following types:
            - ``ModelMetaclass``
            - ``Dict[str, Union[ModelMetaclass, Dict]``
        """
        djagger_method_attributes = http_method.to_djagger_attribute()

        request_body_attr = getattr(view, djagger_method_attributes.BODY_PARAMS.value, None)
        if not request_body_attr: 
            self.requestBody = None
            return

        # Case where a pydantic model is passed, assumes only one media type i.e. application/json
        if isinstance(request_body_attr, ModelMetaclass):
            self.requestBody = RequestBody(
                description = request_body_attr.__doc__,
                content={
                    "application/json":MediaType._from(request_body_attr, component='requestBodies')
                }
            )
            return 
        
        # Case where a dict is passed, extract ``required`` and ``description``
        # and media type for each pair in dict
        elif isinstance(request_body_attr, Dict):

            body = RequestBody()
            body.description = request_body_attr.pop('description', '')
            body.required = request_body_attr.pop('required', False)

            content = {}
            for k, v in request_body_attr:
                
                if isinstance(v, Dict):
                    # validate for MediaType if a dict is given as the value of content
                    content[k] = MediaType(**v)

                elif isinstance(v, ModelMetaclass):
                    content[k] = MediaType._from(v, component='requestBodies') 

                else:
                    raise TypeError("Value in request body dict must be a Dict type or pydantic ModelMetaclass")
                
            body.content = content

            self.requestBody = body
            return

        raise TypeError(f"{djagger_method_attributes.BODY_PARAMS.value} needs to be of type Dict or pydantic ModelMetaclass")


    def _extract_responses(self, view : Type, http_method: HttpMethod):
        ...
        return

    def _extract_security(self, view : Type, http_method: HttpMethod):
        ...
        return

    def _extract_servers(self, view : Type, http_method: HttpMethod):
        ...
        return

    def _extract_deprecated(self, view : Type, http_method: HttpMethod):
        ...
        return

    @classmethod
    def _from(cls, view : Type, http_method : HttpMethod) -> Union['Operation', None]:
        """ Extract attributes from a view class to instantiate Operation given the type of http method for the Operation.
        Wil return None if exclude attribute is True.
        """
        
        operation = cls(
            tags = [],
            summary = "",
            description = "",
            parameters = [],
            responses = {}
        )

        # Exclude at the method-level if `<http_method>_djagger_exclude` is True
        exclude = getattr(view, http_method.to_djagger_attribute().DJAGGER_EXCLUDE.value, False)
        if exclude:
            return None

        operation._extract_tags(view, http_method)
        operation._extract_summary(view, http_method)
        operation._extract_description(view, http_method)
        operation._extract_request_body(view, http_method)
        operation._extract_parameters(view, http_method)
        operation._extract_responses(view, http_method)

        return operation

class Path(BaseModel):
    summary : str = ""
    description : str = ""
    get : Optional[Operation]
    put : Optional[Operation]
    post : Optional[Operation]
    delete : Optional[Operation]
    options : Optional[Operation]
    head : Optional[Operation]
    patch : Optional[Operation]
    trace : Optional[Operation]
    servers : Optional[List[Server]]
    parameters : List[Union[Parameter, Reference]] = []


    @classmethod
    def create(cls, view : Type) -> 'Path':
        """ Given a Class-based view or a function based view, create the Path object 
        from the Djagger attributes set in the view.
        """
        path = cls(
            summary = getattr(view, 'summary', ''),
            description = getattr(view, 'description', '')
        )
        
        if inspect.isclass(view):
            # For CBV or DRF API, check for methods by looking for get(), post(), patch(), put(), delete() methods
            print("is class")
            for http_method in HttpMethod.__members__.values():
                if hasattr(view, http_method):
                    print(" has method", http_method)
                    if callable(getattr(view, http_method)):
                        print("make operation")
                        operation = Operation._from(view, http_method)
                        if not operation:
                            continue
                        # if not operation.responses:
                        #     warnings.warn(f"{view.__name__} does not have a response schema, will not be documented.")
                            continue

                        setattr(path, http_method, operation)

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

                    operation = Operation._from(view, http_method)
                    if not operation:
                        continue
                    if not operation.responses:
                        continue
                    setattr(path, http_method, operation)

            # For FBVs, check for existence of http methods from the `djagger_http_methods` attribute
            # set by the @schema decorator

            if not hasattr(view, DJAGGER_HTTP_METHODS):
                return path

            for method in getattr(view, DJAGGER_HTTP_METHODS, []):
                http_method = HttpMethod(method.lower())
                operation = Operation._from(view, http_method)
                if not operation:
                    continue
                if not operation.responses:
                    continue
                setattr(path, http_method, operation)

        return path


class Components(BaseModel):
    # Replaces Definitions in Swagger 2.0

    schemas : Dict[str, Dict] = {}
    responses : Dict[str, Union[Response, Reference]] = {}
    parameters : Dict[str, Union[Parameter, Reference]] = {}
    examples : Dict[str, Union[Example, Reference]] = {}
    requestBodies : Dict[str, Union[RequestBody, Reference]] = {}
    headers : Dict[str, Union[Header, Reference]] = {}
    securitySchemes : Dict[str, Union[SecurityScheme, Reference]] = {}
    # links : Dict[str, Union[,Reference]] = {}
    callbacks : Dict[str, Dict[str, Dict[str, Union[Path, Reference]]]] = {}

    @classmethod
    def extract_component_schema(cls, model : ModelMetaclass, component : str) -> dict:
        """ Calls the ``.schema()`` method with a custom ``ref_template`` containing uuid4.
        This ensures the generated schema object definition will be unique across all other objects
        if there are duplicate model names (e.g., imported from other modules)

        Builds the component definition $ref according to the component paths

        """
        component_names = cls.__fields__.keys()

        if component not in component_names:
            raise ValueError(f"component value must be one of {str(list(component_names))}. Value provided: {component}")

        suffix = uuid.uuid4().hex
        ref_template = f'#/components/{component}/{{model}}-{suffix}'
        schema = model.schema(ref_template=ref_template)
        definitions = schema.get('definitions', {})
        
        # Change all keys in the component definition to have the suffix as well so the $ref will be valid.
        if definitions:
            schema['definitions'] = { k + '-' + suffix : v for k,v in definitions.items() }

        return schema
        

class Document(BaseModel):

    openapi : str = "3.0.0"
    info : Info = Info()
    servers : List[Server] = []
    paths : Dict[str, Path] = {}
    components : Components = Components()
    security : List[SecurityRequirement] = []
    tags : List[Tag] = []
    externalDocs : Optional[ExternalDocs]

    @classmethod
    def generate(
        cls,
        app_names : List[str] = [],
        tags : List[Tag] = [],
        openapi = "3.0.0",
        version = "1.0.0",
        servers : List[Server] = [],
        title = "Djagger OpenAPI Documentation",
        description = "",
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
            
            if hasattr(view, DjaggerAPIAttributes.DJAGGER_EXCLUDE.value):
                # Exclude generating docs for views with `djagger_exclude=True`
                if view.djagger_exclude:
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
            openapi=openapi,
            info=info,
            servers=servers,
            tags=tags,
            paths=paths,
            x_tag_groups=x_tag_groups,
        )

        # document.compile_definitions()

        return document.dict(by_alias=True, exclude_none=True)
