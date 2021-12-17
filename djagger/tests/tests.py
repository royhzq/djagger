from rest_framework.views import APIView
from rest_framework.response import Response
from django.test import TestCase

from ..openapi import Document

def test_document():
    Document.generate()