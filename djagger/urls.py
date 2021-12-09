from django.urls import path
from .views import *

urlpatterns = [
    path('api/docs', api_doc, name='api_doc'),
    path('api/open-api',open_api_json, name='open_api_json')
]
 