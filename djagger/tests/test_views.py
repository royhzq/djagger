from django.test import TestCase
from django.http import HttpRequest
from django.conf import settings
from django.urls import get_resolver

from ..views import open_api_json, redoc
from ..utils import get_url_patterns

import json
import os, sys

# Set path to 'example' Django project
example_project_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "example")
os.chdir(example_project_path)
sys.path.append(os.getcwd())
os.environ["DJANGO_SETTINGS_MODULE"] = "example.settings"

# Setup 'example' Django project
import django
django.setup()

def test_get_apps():
    assert get_url_patterns(['app1', 'app2'])


def test_open_api_json():

    request = HttpRequest()
    response = open_api_json(request)
    data = json.loads(response.content)
    assert response.status_code == 200
    assert data['info']['title'] == 'DJAGGER_TITLE' # set in example.settings
    assert data['info']['description'] == 'DJAGGER_DESCRIPTION' # set in example.settings
    # print(json.dumps(data))

def test_redoc():

    request = HttpRequest()
    response = redoc(request)
    assert response.status_code == 200


