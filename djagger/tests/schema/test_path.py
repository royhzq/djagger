from pydantic import BaseModel

from ...schema import (
    DjaggerPath
)


def test_exclude_endpoint():

    """ Test the exclusion of endpoint documentation
    """

    class Schema(BaseModel):
        value1: str

    class View:

        response_schema = Schema

        def get(self):
            return None
        def post(self):
            return None

    # No exclusion
    path = DjaggerPath.create(View)
    assert path.get
    assert path.post

    # Exclude get
    View.get_djagger_exclude = True
    path = DjaggerPath.create(View)
    assert path.get == None
    assert path.post

    # Exclude post
    del View.get_djagger_exclude
    View.post_djagger_exclude = True
    path = DjaggerPath.create(View)
    assert path.get 
    assert path.post == None

