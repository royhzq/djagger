from django.urls import path
from .views import *

urlpatterns = [
    path('api/docs', api_doc, name='api_doc'),
    path('api/pet_store', pet_store_json, name='pet_store_json'),
    path('api/open_api',open_api_json, name='open_api_json')
]
 