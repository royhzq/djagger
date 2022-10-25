from rest_framework import fields, serializers
from typing import List, Dict, Optional, Union, Tuple, Type, Any
from pydantic.main import ModelMetaclass
from pydantic import BaseModel, create_model
from decimal import Decimal
from enum import Enum


def field_to_pydantic_args(f: fields.Field) -> Dict:

    """Given a DRF Field, returns a dictionary of arguments to be passed
    to pydantic.create_model() field configs.
    """

    args: Dict = {}

    if hasattr(f, "label"):
        args["alias"] = f.label

    if hasattr(f, "help_text"):
        args["description"] = f.help_text

    if hasattr(f, "read_only"):
        args["readOnly"] = f.read_only

    if hasattr(f, "write_only"):
        args["writeOnly"] = f.write_only

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
        args["enum"] = f.choices

    return args


class SerializerConverter(BaseModel):

    """Converter serializer instance of type ``Serializer`` or ``ListSerializer`` into a pydantic model.
    If metaclass type ``SerializerMetaclass`` detected, converter will call an instance of the serializer to
    instantiate to `Serializer`` type.
    """

    s: Union[
        serializers.SerializerMetaclass,
        serializers.Serializer,
        serializers.ListSerializer,
    ]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def infer_field_type(cls, field: fields.Field, field_name: str):
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
            return cls.from_serializer(field)

        # Handle DictField
        if type(field) == fields.DictField:
            if hasattr(field, "child"):
                t = cls.infer_field_type(field.child, field_name)
                return Dict[str, t]  # type: ignore

        # Handle ChoiceField and MultipleChoiceField - represent as Enum
        if (
            type(field) == fields.ChoiceField
            or type(field) == fields.MultipleChoiceField
        ):
            if hasattr(field, "choices"):
                choices: List[Any] = list(field.choices.keys())
                choice_map: Dict[str, Any] = {str(i): v for i, v in enumerate(choices)}
                # dynamically creating Enum types through the dict literal argument
                # to allow for mixed types in the Enum
                return Enum(field_name, choice_map)  # type: ignore

        return mappings.get(type(field))

    @classmethod
    def from_list_serializer(cls, s: serializers.ListSerializer) -> ModelMetaclass:

        """Converts a DRF ListSerializer into a pydantic model.
        This is used when the parent serializer is a ListSerializer instead of a Serializer.
        """
        name = s.__class__.__name__
        child_model = cls.from_serializer(s.child)

        class Config:
            fields: Dict = {"__root__": {}}

        if hasattr(s, "max_length"):
            Config.fields["__root__"].update({"max_items": s.max_length})

        if hasattr(s, "min_length"):
            Config.fields["__root__"].update({"min_items": s.min_length})

        model = create_model(name, __root__=(List[child_model], ...), __config__=Config)  # type: ignore
        model.__doc__ = s.__doc__

        return model  # type: ignore

    @classmethod
    def from_serializer(cls, s: serializers.Serializer) -> ModelMetaclass:

        """Converts an instance of a DRF Serializer into a pydantic model."""

        name = s.__class__.__name__

        create_model_args = {}  # to be passed into pydantic.create_model

        # Config to be passed into pydantic.create_model __configs__ param
        class Config:
            fields: Dict = {}
            schema_extra: Dict = {"required": []}  # Handling 'required' in schema extra

        for field_name, field in s.get_fields().items():

            Config.fields[field_name] = {}

            # Handle case where field is a ListSerializer
            # e.g. my_field =  MySerializer(many=True)
            if isinstance(field, serializers.ListSerializer):

                t = List[cls.from_serializer(field.child)]  # type: ignore

                if hasattr(field, "max_length"):
                    Config.fields[field_name].update({"max_items": field.max_length})

                if hasattr(field, "min_length"):
                    Config.fields[field_name].update({"min_items": field.min_length})

            # Handle ListField
            elif isinstance(field, fields.ListField):

                t = List[cls.infer_field_type(field.child, field_name)]  # type: ignore

                if hasattr(field, "max_length"):
                    Config.fields[field_name].update({"max_items": field.max_length})

                if hasattr(field, "min_length"):
                    Config.fields[field_name].update({"min_items": field.min_length})

            else:

                # Handle case where field is a normal serializer
                if hasattr(field, "get_fields"):
                    t = cls.from_serializer(field)
                else:
                    t = cls.infer_field_type(field, field_name)

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

        model = create_model(  # type: ignore
            name, **create_model_args, __config__=Config  # type: ignore
        )
        model.__doc__ = s.__doc__

        return model  # type:ignore

    def to_model(self):

        if isinstance(self.s, serializers.ListSerializer):
            return self.from_list_serializer(self.s)

        if isinstance(self.s, serializers.Serializer):
            return self.from_serializer(self.s)

        if isinstance(self.s, serializers.SerializerMetaclass):
            # Instantiates the serializer to be passed to ``from_serializer``
            return self.from_serializer(self.s())
