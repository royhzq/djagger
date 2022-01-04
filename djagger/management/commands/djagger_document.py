"""Custom manage.py command for generating schema json file"""

from django.core.management.base import BaseCommand
from django.conf import settings
from ...openapi import Document

import json


class Command(BaseCommand):

    help = "Generates Djagger schema JSON file"

    def add_arguments(self, parser):
        parser.add_argument("fname", type=str, help="output file name of JSON schema")

    def handle(self, *args, **options):

        fname = options["fname"]
        doc_settings = getattr(settings, "DJAGGER_DOCUMENT", {})
        document = Document.generate(**doc_settings)

        with open(fname, "w") as f:
            f.write(json.dumps(document))
