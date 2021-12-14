"""
Utility functions
====================================
The core module of Djagger project
"""

from django.apps import apps
from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework import fields, serializers
from typing import List, Type, Callable
from pydantic import create_model
from pydantic.main import ModelMetaclass # Abstract classes derived from BaseModel
from typing import List, Dict, Optional
from decimal import Decimal
from enum import Enum
import warnings
import re

def djagger_method_enum_factory(name: str, method : str) -> Enum:

    """ Factory generate DjaggerMethodAttributes enums that 
    represent the allowable attributes for setting request and response schema objects
    in a view for a particular http method.

    Args:
        name (str): The name of the Enum class that will be created. 
        method (str): The http method name i.e. 'get', 'post', 'put', 'patch'. 
                      `method` will be prefixed to all the enum values upon creation.
    """
    
    attrs = {
        "PATH_PARAMS" : "_path_params",
        "QUERY_PARAMS" : "_query_params",
        "HEADER_PARAMS" : "_header_params",
        "COOKIE_PARAMS" : "_cookie_params",
        "BODY_PARAMS" : "_body_params",
        "RESPONSE_SCHEMA" : "_response_schema",
        "SUMMARY" : "_summary",
        "DESCRIPTION" : "_description",
        "OPERATION_ID" : "_operation_id",
        "TAGS" : "_tags",
        "CONSUMES" : "_consumes",
        "PRODUCES" : "_produces",
    }
    prefixed_attrs = { k: method + v for k, v in attrs.items() } 

    return Enum(name, prefixed_attrs)


def get_url_patterns(app_names : List[str]) -> List[URLPattern]:
    """ Given a list of app names in the project, return a filtered list of URLPatterns that contain a class-based view or Django Rest Framework API class.

    Function-based views are not included in the returned list.

    Args:
        app_names (List[str]): List of app names to retrieve ``URLPattern`` objects from.

    """
    # List of app modules
    resolver_dict = get_resolver().reverse_dict # Make this call to init URLS if this function is used in django shell

    if app_names:
        # if app_names is not empty - only consider apps listed in app_names
        app_list = [apps.app_configs.get(name).module for name in app_names if name in apps.app_configs ] 
    else:
        # else consider all installed apps, less djagger app itself
        app_list = [ app_config.module for app_config in apps.app_configs.values() if app_config.name != 'djagger' ]
    
    url_patterns = [] 

    for app in app_list:
        
        if not hasattr(app, 'urls'):
            continue

        if not hasattr(app.urls, 'urlpatterns'):
            warnings.warn(f"Warning: urlpatterns not found in {app.__name__}")
            continue

        for url_pattern in app.urls.urlpatterns:
            # Must be CBV or Django Rest API class - if no class exists, skip
            if not hasattr(url_pattern, "callback"):
                raise ValueError(f"URL {url_pattern.name} does not have a callback to a view function.")
            
            # Add the attribute _schema_path to each url pattern
            # TODO: Refactor retrieving full URL pattern including prefixes below
            try:
                full_path_pattern = resolver_dict[url_pattern.callback][0][0][0]
                url_pattern._schema_path = clean_resolver_url_pattern(full_path_pattern)
            except:
                warnings.warn(f"get_url_patterns() : Unable to clean schema pattern - {url_pattern.pattern.name}")
                # If unable to get fully formed URL pattern, fallback to getting route pattern
                if hasattr(url_pattern.pattern, '_route'):
                    url_pattern._schema_path = clean_route_url_pattern(url_pattern.pattern._route)
                elif hasattr(url_pattern.pattern, 'regex'):
                    url_pattern._schema_path = url_pattern.pattern.regex.pattern.replace("^", "").replace("$", "")
                else:
                    raise AttributeError("urlpattern does not contain _route or regex. Make sure you are using path() in your url patterns")
                
            url_patterns.append(url_pattern)

    return url_patterns

def clean_resolver_url_pattern(route : str) -> str:
    """ Cleans the full url path pattern from a url resolver into a OpenAPI schema url pattern.

    Args:
        route (str): Full URL path pattern including any prefixed paths.

    Returns:
        str: OpenAPI path format

    Example::

        >>clean_resolver_url_pattern("toy/%(toyId)s/uploadImage")
        toy/{toyId}/uploadImage

    """ 
    return re.sub(r'\%\(([a-zA-Z0-9\-\_]*)\)s', r'{\1}', route)
            
def clean_route_url_pattern(route : str) -> str:
    """ Converts a django path route string format into an openAPI route format.

    Args:
        route (str): URL path pattern from URLPattern object.

    Returns:
        str: OpenAPI path format

    Example::

        >>clean_route_url_pattern("/list/<int:pk>")
        /list/{pk}

    """
    return re.sub(r'<[a-zA-Z0-9\-\_]*:([a-zA-Z0-9\-\_]*)>', r'{\1}', route)

def base_model_set_examples(base_model : ModelMetaclass):
    """ Check if a class has callable `example()` and if so, sets the schema 'example' field
    to the result of `example()` callable. The callable should return an instance of the pydantic base model type.
    `example()` should return a single instance of the pydantic base model type.
    """

    # Where `example()` method exists
    if hasattr(base_model, 'example'):
        if callable(base_model.example):
            base_model.Config.schema_extra['example'] = [base_model.example().dict()]
            base_model.schema()
            return
        base_model.Config.schema_extra['example'] = []
    

def infer_field_type(field : fields.Field):
    """ Classifies DRF Field types into primitive python types or 
    creates an appropriate pydantic model metaclass types if the field itself
    is a Serializer class.
    
    """
    mappings = {
        fields.BooleanField: bool,
        fields.NullBooleanField: bool,
        fields.CharField: str,
        fields.EmailField: str,
        fields.RegexField: str,
        fields.SlugField: str,
        fields.URLField: str,
        fields.UUIDField: str,
        fields.FilePathField: str,
        fields.IPAddressField: str,
        fields.IntegerField: int,
        fields.FloatField: float,
        fields.DecimalField: Decimal,
        fields.DateTimeField: str,
        fields.DateField: str,
        fields.TimeField: str,
        fields.DurationField: str,
        fields.ChoiceField: str,
        fields.MultipleChoiceField: str,
        fields.FileField: str,
        fields.ImageField: str,
        fields.ListField: List,
        fields.DictField: Dict,
        fields.HStoreField: Dict,
        fields.JSONField: str,
    }
    
    # Handle case where nested serializer is a field 
    if hasattr(field, "get_fields"):
        return schema_from_serializer(field)    

    # Handle DictField
    if type(field) == fields.DictField:
        if hasattr(field, 'child'):
            t = infer_field_type(field.child)
            return Dict[str, t]
    
    return mappings.get(type(field))

def field_to_pydantic_args(f : fields.Field) -> Dict:
    
    """ Given a DRF Field, returns a dictionary of arguments to be passed
    to pydantic.create_model() field configs.
    """
    
    args = {
        'extra':{}
    }

    if hasattr(f, 'label'):
        args['alias']=f.label

    if hasattr(f, 'help_text'):        
        args['description']= f.help_text
        
    if hasattr(f, 'read_only'):
        args['extra']['readonly'] = f.read_only

    if hasattr(f, 'write_only'):
        args['extra']['writeonly'] = f.write_only
        
    if hasattr(f, 'format'):
        args['format'] = f.format
        
    # string fields
    if hasattr(f, 'max_length'):
        
        # Avoid clashing with ListSerializer or ListField max_length property
        
        if isinstance(f, serializers.ListSerializer):
            pass
        elif isinstance(f, fields.ListField):
            pass
        else:
            args['max_length'] = f.max_length
        
    if hasattr(f, 'min_length'):
        # Avoid clashing with ListSerializer or ListField min_length property
        if isinstance(f, serializers.ListSerializer):
            pass
        elif isinstance(f, fields.ListField):
            pass
        else:
            args['min_length'] = f.min_length

    if hasattr(f, 'uuid_format'):
        args['format'] = f.uuid_format
        
    #TODO: Handle regex field format

    # numeric fields
    if hasattr(f, 'max_value'):
        args['lt'] = f.max_value
        
    if hasattr(f, 'min_value'):
        args['gt'] = f.min_value
        
    # choice fields
    if hasattr(f, 'choices'):
        # choices attr is a list of (key, display_name) tuples.
        args['extra']['choices'] = f.choices
        
    return args
    
def schema_from_serializer(s : serializers.Serializer) -> ModelMetaclass:

    """ Converts a DRF Serializer type into a pydantic model.
    """

    name = s.__class__.__name__
        
    create_model_args = {} # to be passed into pydantic.create_model
    
    # Config to be passed into pydantic.create_model __configs__ param
    class Config:
        fields = {}
        schema_extra={
            'required':[] # Handling 'required' in schema extra
        }
            
    for field_name, field in s.get_fields().items():
        
        Config.fields[field_name] = {}
        
        # Handle case where field is a ListSerializer
        #i.e. my_field =  MySerializer(many=True)
        if isinstance(field, serializers.ListSerializer):
            
            t = List[schema_from_serializer(field.child)]
            
            if hasattr(field, 'max_length'):
                Config.fields[field_name].update({'max_items':field.max_length})
            
            if hasattr(field, 'min_length'):
                Config.fields[field_name].update({'min_items':field.min_length})
        
        # Handle ListField
        elif isinstance(field, fields.ListField):
        
            t = List[infer_field_type(field.child)]
            
            if hasattr(field, 'max_length'):
                Config.fields[field_name].update({'max_items':field.max_length})
            
            if hasattr(field, 'min_length'):
                Config.fields[field_name].update({'min_items':field.min_length})
                
        else:
            
            # Handle case where field is a normal serializer         
            if hasattr(field, 'get_fields'):
                t = schema_from_serializer(field)
            else:
                t = infer_field_type(field)

        default = ...
        
        if field.default != fields.empty:
            default = field.default
            
        if field.required:    
            # DRF does not allow setting both `required` and `default`
            # So if field is required, pass ... as the default value
            create_model_args[field_name] = (t, ...)
            Config.schema_extra['required'].append(field_name)
        else:
            create_model_args[field_name] = (Optional[t], default)
            
        Config.fields[field_name].update(field_to_pydantic_args(field))
    
    model = create_model(name, **create_model_args, __config__=Config)
        
    return model