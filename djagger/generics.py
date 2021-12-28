""" Utils to help extract serializers from Generic DRF Views
"""
from rest_framework.serializers import SerializerMetaclass, ListSerializer
from .enums import ViewAttributes

def set_response_schema_from_serializer_class(view):
    """Given a View, set ``response_schema`` if it has not been set to the value in ``serializer_class``
    , provided that the ``serializer_class`` value is a ``rest_framework.serializers.SerializerMetaclass`` type.

    This is to give ``GenericAPIView`` views a default response schema by using the ``serializer_class``.
    """

    if not hasattr(view, 'serializer_class'):
        return 

    if not isinstance(view.serializer_class, (SerializerMetaclass, ListSerializer)):
        return

    if hasattr(view, ViewAttributes.api.RESPONSE_SCHEMA):
        # skip if response_schema was already set
        return 

    view.response_schema = view.serializer_class
    return

    




