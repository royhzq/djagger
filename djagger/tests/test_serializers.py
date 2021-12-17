""" Tests the conversion of DRF Serializers to pydantic models
"""

from rest_framework import fields, serializers
from ..serializers import SerializerConverter

def test_all_primiitive_fields():

    # Test serializer with basic field types
    # No nested serializers

    class TestSerializer(serializers.Serializer):

        booleanfield = fields.BooleanField()
        charfield = fields.CharField()
        emailfield = fields.EmailField()
        regexfield = fields.RegexField(regex="")
        slugfield = fields.SlugField()
        urlfield = fields.URLField()
        uuidfield = fields.UUIDField()
        filepathfield = fields.FilePathField(path="/")
        ipaddressfield = fields.IPAddressField()
        integerfield = fields.IntegerField()
        floatfield = fields.FloatField()
        decimalfield = fields.DecimalField(max_digits=3, decimal_places=2)
        datetimefield = fields.DateTimeField()
        datefield = fields.DateField()
        timefield = fields.TimeField()
        durationfield = fields.DurationField()
        choicefield = fields.ChoiceField(choices=[('a','a')])
        multiplechoicefield = fields.MultipleChoiceField(choices=[('a','a')])
        filefield = fields.FileField()
        imagefield = fields.ImageField()

        listfield = fields.ListField(child=fields.CharField())
        dictfield = fields.DictField()
        hstorefield = fields.HStoreField()
        jsonfield = fields.JSONField()


    model = SerializerConverter(s=TestSerializer()).to_model()

    assert model.schema()


def test_nested_serializers():

    class Nested(serializers.Serializer):
        field = fields.CharField()

    class TestSerializer(serializers.Serializer):
        nested = Nested()

    model = SerializerConverter(s=TestSerializer()).to_model()

    assert model.schema()

def test_nested_serializers_many():

    class Nested(serializers.Serializer):
        field = fields.CharField()

    class TestSerializer(serializers.Serializer):
        nested = Nested(many=True)

    model = SerializerConverter(s=TestSerializer()).to_model()

    assert model.schema()
    
def test_nested_list_fields():

    class L2(serializers.Serializer):
        char = fields.CharField()
        number = fields.IntegerField()

    class L1(serializers.Serializer):
        l_1 = L2(many=True)

    class L0(serializers.Serializer):
        l_0 = fields.ListField(child=L1(), min_length=4)

    class TestSerializer(serializers.Serializer):
        listfield = fields.ListField(child=L0(), max_length=12)

    model = SerializerConverter(s=TestSerializer()).to_model()
    assert model.schema()
    
def test_list_serializer():

    class TestSerializer(serializers.Serializer):
        pk = fields.IntegerField()        

    model = SerializerConverter(s=TestSerializer(many=True), max_length=4).to_model()
    assert model.schema()

    # Directly from ListSerializer
    model = SerializerConverter(
        s=serializers.ListSerializer(
            child=TestSerializer()
        )
    ).to_model()
    assert model.schema()


from ..openapi import Document

def test_document():
    Document.generate()