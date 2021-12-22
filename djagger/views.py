from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.conf import settings

from .decorators import schema
from .openapi import Document as OpenAPIDoc

import os

@schema(methods=['GET'], djagger_exclude=True)
def open_api_json(request : HttpRequest):

    """ View for auto generated OpenAPI JSON document 
    """
    document = OpenAPIDoc.generate(
        app_names = getattr(settings, 'DJAGGER_APP_NAMES', []),
        tags = getattr(settings, 'DJAGGER_TAGS', []),
        openapi = getattr(settings, 'DJAGGER_OPENAPI', "3.0.0"),
        version = getattr(settings, 'DJAGGER_VERSION', "1.0.0"),
        servers = getattr(settings, 'DJAGGER_SERVERS', []),
        security = getattr(settings, 'DJAGGER_SECURITY', []),
        title = getattr(settings, 'DJAGGER_TITLE', "Djagger OpenAPI Documentation"),
        description = getattr(settings, 'DJAGGER_DESCRIPTION', ""),
        terms_of_service = getattr(settings, 'DJAGGER_TERMS_OF_SERVICE', ""),
        contact_name = getattr(settings, 'DJAGGER_CONTACT_NAME', ""),
        contact_email = getattr(settings, 'DJAGGER_CONTACT_EMAIL', ""),
        contact_url = getattr(settings, 'DJAGGER_CONTACT_URL', ""),
        license_name = getattr(settings, 'DJAGGER_LICENSE_NAME', ""),
        license_url = getattr(settings, 'DJAGGER_LICENSE_URL', ""),
        x_tag_groups = getattr(settings, 'DJAGGER_X_TAG_GROUPS', [])
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

    basepath = os.path.dirname(__file__)
    template_path = os.path.abspath(os.path.join(basepath, "templates/redoc.html"))
    with open(template_path, "r") as t:
        html = t.read()

    response = HttpResponse(html, content_type="text/html")
    
    return response
