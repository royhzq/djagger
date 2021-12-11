from django.urls import path
from .views import redoc, open_api_json

urlpatterns = [
    path('api/docs', redoc, name='djagger_doc'),
    path('schema.json',open_api_json, name='djagger_json')
]
 