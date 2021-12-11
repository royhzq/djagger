from django.urls import path
from .views import *

urlpatterns = [
    path("example_fbv_view", example_fbv_view, name="example_fbv_view"),
    path("example_cbv_view", CBVView.as_view(), name="example_cbv_view")
]