from django.test import TestCase
from django.http import HttpRequest
from django.conf import settings
from ..views import open_api_json, redoc

import json


DJAGGER_TITLE = "Test OpenAPI View"
DJAGGER_DESCRIPTION = "Test OpenAPI Description"

settings.configure(
    ROOT_URLCONF='djagger.tests.urls',
    DJAGGER_TITLE = DJAGGER_TITLE,
    DJAGGER_DESCRIPTION = DJAGGER_DESCRIPTION
)

def test_open_api_json():

    request = HttpRequest()
    response = open_api_json(request)
    data = json.loads(response.content)
    assert data['info']['title'] == DJAGGER_TITLE
    assert data['info']['description'] == DJAGGER_DESCRIPTION

def test_redoc():

    request = HttpRequest()
    response = redoc(request)
    assert response.status_code == 200


