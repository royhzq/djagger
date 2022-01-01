from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.conf import settings
from django.urls import reverse

from .decorators import schema
from .openapi import Document as OpenAPIDoc

import os


@schema(methods=["GET"], djagger_exclude=True)
def open_api_json(request: HttpRequest):
    """ View for auto generated OpenAPI JSON document """

    doc_settings = getattr(settings, "DJAGGER_DOCUMENT", {})
    document = OpenAPIDoc.generate(**doc_settings)

    response = JsonResponse(document)
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response


@schema(methods=["GET"], djagger_exclude=True)
def redoc(request: HttpRequest):
    """Redoc openAPI document that is initialized from the JSON output of
    open_api_json()
    See https://github.com/Redocly/redoc
    """
    return render(request, "djagger/redoc.html")
