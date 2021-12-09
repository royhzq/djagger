from django.urls import path
from .views import *

urlpatterns = [
    path("example_fbv_view", example_fbv_view, name="example_fbv_view")
]