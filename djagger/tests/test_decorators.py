from ..decorators import schema
from ..enums import DJAGGER_HTTP_METHODS

def test_schema_decorator_1():

    # Test successful setting of FBV attributes via decorator

    methods = ["get", "post", "PUT"]
    summary = "Test Decorator View"

    @schema(methods=methods, summary=summary)
    def fbv():
        return None

    assert fbv.summary == summary
    assert getattr(fbv, DJAGGER_HTTP_METHODS) == methods

def test_schema_decorator_2():

    # Test invalid http methods passed
    
    error = None
    try:
        @schema(methods=["wrong"])
        def fbv():
            return None
    except ValueError as e:
        error = e
    
    assert error
