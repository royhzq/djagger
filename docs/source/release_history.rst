Release History
===============

1.1.3
-----

**Fixed**

* Fixed bug where authorizations and security schemes were not being rendered. ``components`` parameter passed was not being proceessed in ``Document.generate``.

1.1.2
-----

**Added**

* Added ``url_names`` parameter to ``get_url_patterns`` to allow ``DJAGGER_DOCUMENT`` to filter API endpoints that should be documented via their url names.
* Added missing ``.gitignore`` file.

**Fixed**

* Fixed date typos in this changelog file.


1.1.1
-----

**Added**

* Rest framework ``serializers.ChoiceField`` and ``serializers.MultipleChoiceField`` will now be represented as ``Enum`` types with enum values correctly reflected in the schema.
* Documentation for using Tags.

**Fixed**

* Fix bug where schema examples are not generated correctly.
* Fix bug where the request URL for the objects are generated with an incorrect prefix.


1.1.0
-----

**Added**

* Added documentation.
* Support for generic views and viewsets.
* Support for DRF Serializer to pydantic model conversion.
* Support for multiple responses and different response content types.
* Support for function-based views via ``schema`` decorator.
* Added option for a global prefix to all Djagger attributes.
* Generated schema fully compatible with OpenAPI 3.

**Removed**

* ``djagger.swagger.*`` pydantic models. Removed support for Swagger 2.0 specification.