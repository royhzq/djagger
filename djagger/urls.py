from django.urls import path
from .views import redoc, open_api_json

urlpatterns = [
    path('api/docs', redoc, name='api_doc'),
    path('api/open-api',open_api_json, name='open_api_json')
]
 