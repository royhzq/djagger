import pytest
from django.conf import settings
import django

@pytest.fixture(scope="session", autouse=True)
def setup(request):

    # prepare django ahead of all tests

    settings.configure()
    django.setup()


