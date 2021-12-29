from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.conf import settings
from django.urls import reverse

from .decorators import schema
from .openapi import Document as OpenAPIDoc

import os

@schema(methods=['GET'], djagger_exclude=True)
def open_api_json(request : HttpRequest):
    """ View for auto generated OpenAPI JSON document """

    doc_settings = getattr(settings, 'DJAGGER_DOCUMENT', {})

    document = OpenAPIDoc.generate(
        app_names = doc_settings.get('app_names', []),
        tags = doc_settings.get('tags', []),
        openapi = doc_settings.get('openapi', "3.0.0"),
        version = doc_settings.get('version', "1.0.0"),
        servers = doc_settings.get('servers', []),
        security = doc_settings.get('security', []),
        title = doc_settings.get('title', "Djagger OpenAPI Documentation"),
        description = doc_settings.get('description', ""),
        terms_of_service = doc_settings.get('terms_of_service', ""),
        contact_name = doc_settings.get('contact_name', ""),
        contact_email = doc_settings.get('contact_email', ""),
        contact_url = doc_settings.get('contact_url', ""),
        license_name = doc_settings.get('license_name', ""),
        license_url = doc_settings.get('license_url', ""),
        x_tag_groups = doc_settings.get('x_tag_groups', [])
    )
    
    response = JsonResponse(document)
    response['Cache-Control'] = "no-cache, no-store, must-revalidate"
    return response

@schema(methods=['GET'], djagger_exclude=True)
def redoc(request : HttpRequest):
    """ Redoc openAPI document that is initialized from the JSON output of 
    open_api_json()
    See https://github.com/Redocly/redoc
    """
    return render(request, 'djagger/redoc.html')