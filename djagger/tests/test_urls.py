from django.urls import get_resolver
from django.conf import settings
from ..utils import clean_regex_string

def test_clean_regex():

    urls= [
        '^toy\\/^', 
        '^toy\\/^findByStatus', 
        '^toy\\/^findByTags', 
        '^toy\\/^(?P<toyId>[0-9]+)', 
        '^toy\\/^(?P<toyId>[0-9]+)\\/uploadImage', 
        '^store\\/^inventory', 
        '^store\\/^order', 
        '^store\\/^order\\/(?P<orderId>[0-9]+)', 
        '^^order_sets/$', 
        '^^order_sets\\.(?P<format>[a-z0-9]+)/?$', 
        '^^order_sets/(?P<pk>[^/.]+)/$', 
        '^^order_sets/(?P<pk>[^/.]+)\\.(?P<format>[a-z0-9]+)/?$', 
        '^^$', 
        '^^\\.(?P<format>[a-z0-9]+)/?$',    
        '^user\\/^', 
        '^user\\/^createWithList', 
        '^user\\/^login', 
        '^user\\/^logout', 
        '^user\\/^(?P<username>[^/]+)', 
        '^djagger\\/^api\\/docs', 
        '^djagger\\/^schema\\.json'
    ]

    for url in urls:
        clean = clean_regex_string(url)

    assert clean
