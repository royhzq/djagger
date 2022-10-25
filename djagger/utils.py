"""
Utility functions
====================================
The core module of Djagger project
"""

from django.apps import apps
from django.urls import URLPattern, URLResolver, get_resolver
from django.urls.resolvers import RegexPattern, RoutePattern, _route_to_regex
from rest_framework import fields, serializers
from typing import List, Type, Callable, Any
from pydantic import create_model
from pydantic.main import ModelMetaclass, ModelField
from pydantic.fields import UndefinedType
from pydantic.schema import get_flat_models_from_model, get_model_name_map, field_schema
from typing import List, Dict, Optional, Union, Tuple
from decimal import Decimal
from enum import Enum
import warnings
import re
import uuid


def get_app_name(module: str) -> str:
    """Given the value of ``__module__`` dunder attr, return the
    name of the top level module i.e. the app name.

    Example::

        >>get_app_name('MyApp.urls.resolvers')
        'MyApp'

    """

    return module.split(".")[0]


def clean_resolver_url_pattern(route: str) -> str:
    """Cleans the full url path pattern from a url resolver into a OpenAPI schema url pattern.

    Args:
        route (str): Full URL path pattern including any prefixed paths.

    Returns:
        str: OpenAPI path format

    Example::

        >>clean_resolver_url_pattern("toy/%(toyId)s/uploadImage")
        toy/{toyId}/uploadImage

    """
    return re.sub(r"\%\(([a-zA-Z0-9\-\_]*)\)s", r"{\1}", route)


def clean_route_url_pattern(route: str) -> str:
    """Converts a django path route string format into an openAPI route format.

    Args:
        route (str): URL path pattern from URLPattern object.

    Returns:
        str: OpenAPI path format

    Example::

        >>clean_route_url_pattern("/list/<int:pk>")
        /list/{pk}

    """
    return re.sub(r"<[a-zA-Z0-9\-\_]*:([a-zA-Z0-9\-\_]*)>", r"{\1}", route)


def clean_regex_string(s: str) -> str:
    """Converts regex string pattern for a path into OpenAPI format.

    Example::

        >>s = '^toy\\/^(?P<toyId>[a-zA-Z0-9-_]+)\\/details'
        >>clean_regex_string(s)
        'toy/{toyId}/details'

    """
    s = s.replace("^", "").replace("\\", "")
    regex_pattern = r"\(\?P<([a-zA-Z0-9-_]*)>.*?\)"
    return re.sub(regex_pattern, r"{\1}", s).replace("?", "").replace("$", "")


def get_pattern_str(pattern: Union[RegexPattern, RoutePattern]) -> str:
    """Given a URLPattern.pattern, or a URLResolver.pattern, return
    the path string in regex form.

    A pattern can exist as ``RegexPattern`` or ``RoutePattern``. The
    string returned will be in the regex pattern form for consistency
    """

    if isinstance(pattern, RegexPattern):
        return pattern._regex

    elif isinstance(pattern, RoutePattern):
        return _route_to_regex(pattern._route)[0]

    raise TypeError(
        f"pattern is of type {type(pattern)}. Needs to be RegexPattern or RoutePattern"
    )


def list_urls(resolver: URLResolver, prefix="") -> List[Tuple[str, URLPattern]]:

    """Returns a list of tuples containing the 'cleaned' full url path and the
    corresponding URLPattern object
    """

    urls = resolver.url_patterns

    results = []

    for url in urls:
        if isinstance(url, URLResolver):
            nested_results = list_urls(url, prefix=get_pattern_str(url.pattern))
            results += nested_results
            continue

        url_pattern = prefix + get_pattern_str(url.pattern)
        results.append((clean_regex_string(url_pattern), url))

    return results


def get_url_patterns(
    app_names: List[str], url_names: List[str] = []
) -> List[Tuple[str, URLPattern]]:
    """Given a list of app names in the project, return a filtered list of URLPatterns that contains a view function or class
    that are part of the listed apps. Include all apps, less ``djagger`` if ``app_names`` is an empty list.

    If ``url_names`` is provided, will further filter the list to only include URLPatterns that match the URL names as provided in the ``url_names`` list.
    """
    # List of app modules
    results = []

    for path, url_pattern in list_urls(get_resolver()):

        if not hasattr(url_pattern, "callback"):
            continue

        if not url_pattern.callback:
            continue

        path_app_name = get_app_name(url_pattern.callback.__module__)

        if path_app_name == "djagger":
            continue

        if app_names:

            if path_app_name not in app_names:
                continue
        if url_names:
            if url_pattern.name not in url_names:
                continue

        results.append((path, url_pattern))

    return results


def schema_set_examples(schema: Dict, model: Any):
    """Check if a class has callable `example()` and if so, sets the schema 'example' field
    to the result of `example()` callable. The callable should return an instance of the pydantic base model type.
    `example()` should return a single instance of the pydantic base model type.
    """
    if hasattr(model, "example"):
        if callable(model.example):
            schema["example"] = model.example().json(by_alias=True)
    return schema


def infer_field_type(field: fields.Field):
    """Classifies DRF Field types into primitive python types or
    creates an appropriate pydantic model metaclass types if the field itself
    is a Serializer class.
    """
    mappings = {
        fields.BooleanField: bool,
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
        if hasattr(field, "child"):
            t = infer_field_type(field.child)
            return Dict[str, t]  # type: ignore

    return mappings.get(type(field))


def field_to_pydantic_args(f: fields.Field) -> Dict:
    """Given a DRF Field, returns a dictionary of arguments to be passed
    to pydantic.create_model() field configs.
    """

    args: Dict = {"extra": {}}

    if hasattr(f, "label"):
        args["alias"] = f.label

    if hasattr(f, "help_text"):
        args["description"] = f.help_text

    if hasattr(f, "read_only"):
        args["extra"]["readonly"] = f.read_only

    if hasattr(f, "write_only"):
        args["extra"]["writeonly"] = f.write_only

    if hasattr(f, "format"):
        args["format"] = f.format

    # string fields
    if hasattr(f, "max_length"):

        # Avoid clashing with ListSerializer or ListField max_length property

        if isinstance(f, serializers.ListSerializer):
            pass
        elif isinstance(f, fields.ListField):
            pass
        else:
            args["max_length"] = f.max_length

    if hasattr(f, "min_length"):
        # Avoid clashing with ListSerializer or ListField min_length property
        if isinstance(f, serializers.ListSerializer):
            pass
        elif isinstance(f, fields.ListField):
            pass
        else:
            args["min_length"] = f.min_length

    if hasattr(f, "uuid_format"):
        args["format"] = f.uuid_format

    # TODO: Handle regex field format

    # numeric fields
    if hasattr(f, "max_value"):
        args["lt"] = f.max_value

    if hasattr(f, "min_value"):
        args["gt"] = f.min_value

    # choice fields
    if hasattr(f, "choices"):
        # choices attr is a list of (key, display_name) tuples.
        args["extra"]["choices"] = f.choices

    return args


def schema_from_serializer(s: serializers.Serializer) -> ModelMetaclass:

    """Converts a DRF Serializer type into a pydantic model."""

    name = s.__class__.__name__

    create_model_args = {}  # to be passed into pydantic.create_model

    # Config to be passed into pydantic.create_model __configs__ param
    class Config:
        fields: Dict = {}
        schema_extra: Dict = {"required": []}  # Handling 'required' in schema extra

    for field_name, field in s.get_fields().items():

        Config.fields[field_name] = {}

        # Handle case where field is a ListSerializer
        # i.e. my_field =  MySerializer(many=True)
        if isinstance(field, serializers.ListSerializer):

            t = List[schema_from_serializer(field.child)]  # type: ignore

            if hasattr(field, "max_length"):
                Config.fields[field_name].update({"max_items": field.max_length})

            if hasattr(field, "min_length"):
                Config.fields[field_name].update({"min_items": field.min_length})

        # Handle ListField
        elif isinstance(field, fields.ListField):

            t = List[infer_field_type(field.child)]  # type: ignore

            if hasattr(field, "max_length"):
                Config.fields[field_name].update({"max_items": field.max_length})

            if hasattr(field, "min_length"):
                Config.fields[field_name].update({"min_items": field.min_length})

        else:

            # Handle case where field is a normal serializer
            if hasattr(field, "get_fields"):
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
            Config.schema_extra["required"].append(field_name)
        else:
            create_model_args[field_name] = (Optional[t], default)

        Config.fields[field_name].update(field_to_pydantic_args(field))

    model: ModelMetaclass = create_model(name, **create_model_args, __config__=Config)  # type: ignore

    return model


def model_field_schemas(
    model: Any,
) -> List[Tuple[Dict, Dict]]:
    """Returns list of tuple with a JSON Schema for it as the first item.
    Also return a dictionary of definitions with models as keys and their schemas as values.
    Refer to ``pydantic.fields.field_schema`` for reference
    """
    schemas = []
    flat_models = get_flat_models_from_model(model)
    model_name_map = get_model_name_map(flat_models)

    for model_field in model.__fields__.values():

        schema, definitions, _ = field_schema(
            field=model_field,
            by_alias=True,
            model_name_map=model_name_map,
            ref_template="#/definitions/{model}",
        )
        schema["title"] = model_field.alias
        schemas.append((schema, definitions))

    return schemas


# def extract_unique_schema(model : ModelMetaclass) -> dict:
#     """ Calls the ``.schema()`` method with a custom ``ref_template`` containing uuid4.
#     This ensures the generated schema object definition will be unique across all other objects
#     if there are duplicate model names (e.g., imported from other modules)
#     """
#     suffix = uuid.uuid4().hex
#     schema = model.schema(ref_template='#/definitions/{model}' + '-' + suffix)
#     definitions = schema.get('definitions', {})

#     # Change all keys in definitions to have the suffix as well so the $ref will be valid.
#     if definitions:
#         schema['definitions'] = { k + '-' + suffix : v for k,v in definitions.items() }

#     return schema
