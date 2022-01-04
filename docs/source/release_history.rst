Release History
===============

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