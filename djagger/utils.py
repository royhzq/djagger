from django.apps import apps
from django.urls import URLPattern, URLResolver, get_resolver
from typing import List, Type
from pydantic.main import ModelMetaclass # Abstract classes derived from BaseModel

from enum import Enum
import warnings

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
    """
    # List of app modules
    get_resolver().reverse_dict # Make this call to init URLS if this function is used in django shell

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
            url_patterns.append(url_pattern)

    return url_patterns

            
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
    
