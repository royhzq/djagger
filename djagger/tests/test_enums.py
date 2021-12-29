from ..enums import HttpMethod, DjaggerViewAttributes, ViewAttributes

def test_djagger_view_attributes():
    """Test creation of ViewAttributes with custom prefix"""

    custom_prefix = "test_"
    CustomViewAttributes = DjaggerViewAttributes(custom_prefix, *HttpMethod.values())

    for http_method in HttpMethod.values():

        operation_enum = getattr(CustomViewAttributes, http_method)
        for attr in operation_enum.values():
            assert custom_prefix in attr

    for attr in CustomViewAttributes.api.values():
        assert custom_prefix in attr


def test_view_attributes():
    """Test correct creation of ViewAttributes"""
    assert len(ViewAttributes.attr_list) > 0