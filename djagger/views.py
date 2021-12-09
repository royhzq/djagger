from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings

from .decorators import schema
from .types import DjaggerDoc

import os

@schema(methods=['GET'], djagger_exclude=True)
def open_api_json(request):

    """ View for auto generated OpenAPI JSON document 
    """

    app_names = getattr(settings, 'DJAGGER_APP_NAMES', [])
    description = getattr(settings, 'DJAGGER_DESCRIPTION', "")
    contact_name = getattr(settings, 'DJAGGER_CONTACT_NAME', "")
    contact_email = getattr(settings, 'DJAGGER_CONTACT_EMAIL', "")
    contact_url = getattr(settings, 'DJAGGER_CONTACT_URL', "")
    license_name = getattr(settings, 'DJAGGER_LICENSE_NAME', "")
    license_url = getattr(settings, 'DJAGGER_LICENSE_URL', "")
    basePath = getattr(settings, 'DJAGGER_BASEPATH', "")
    tags = getattr(settings, 'DJAGGER_TAGS', "")
    version = getattr(settings, 'DJAGGER_VERSION', "1.0.5")
    title = getattr(settings, 'DJAGGER_TITLE', "Djagger OpenAPI Documentation")
    schemes = getattr(settings, 'DJAGGER_SCHEMES', ['http','https'])
    swagger = getattr(settings, 'DJAGGER_SWAGGER', "2.0")
    host = getattr(settings, 'DJAGGER_HOST', "example.org")
    terms_of_service = getattr(settings, 'DJAGGER_TERMS_OF_SERVICE', "")

    document = DjaggerDoc.generate_openapi(
        app_names=app_names,
        description=description,
        contact_name=contact_name,
        contact_email=contact_email,
        contact_url=contact_url,
        license_name=license_name,
        license_url=license_url,
        basePath=basePath,
        version=version,
        title=title,
        schemes=schemes,
        tags=tags,
        terms_of_service=terms_of_service
    )

    response = JsonResponse(document)
    response['Cache-Control'] = "no-cache, no-store, must-revalidate"
    return response

@schema(methods=['GET'], djagger_exclude=True)
def redoc(request):

    basepath = os.path.dirname(__file__)
    template_path = os.path.abspath(os.path.join(basepath, "templates/redoc.html"))
    with open(template_path, "r") as t:
        html = t.read()

    response = HttpResponse(html, content_type="text/html")
    
    return response
