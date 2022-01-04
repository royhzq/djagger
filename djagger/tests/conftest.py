from django.conf import settings
from typing import List
import pytest
import django

urlpatterns: List = []


@pytest.fixture(scope="session", autouse=True)
def setup(request):
    # prepare django ahead of all tests
    settings.configure(ROOT_URLCONF=__name__)
    django.setup()
