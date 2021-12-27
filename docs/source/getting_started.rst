Getting Started
===============

Installation
------------

Install using ``pip``

.. code:: bash

    pip install djagger

Add ``djagger`` to your ``INSTALLED_APPS`` setting in your Django project like this:

.. code:: python

    INSTALLED_APPS = [
        ...
        'djagger',
    ]
  

Include the djagger URLconf in your project ``urls.py`` like this if you want to use the built-in document views.

.. code:: python

    urlpatterns = [
        ...
        path('djagger/', include('djagger.urls')),
    ]

.. NOTE::
   * To see the generated documentation, use the route **/djagger/api/docs**. Djagger uses `Redoc <https://github.com/Redocly/redoc>`_ as the default client generator.       
   * To get the generated JSON schema file, use the route **/djagger/schema.json**.                                                                                           


The path ``djagger/`` is not compulsory when setting this configuration. Replace ``djagger/`` with your preferred route prefix. For customized control over the documentation views, free to remove ``djagger.urls`` and write your own views. The routes provided here are for you to get started quickly.


Package Overview
----------------

Djagger is a pydantic-based Django package that automates the documentation of APIs. The documentation generated is OpenAPI 3 compliant. Djagger seeks to simplify the documentation process while providing a high degree of customization for the generated documentation, all without adding too much bloat to your existing codebase. 

Features
--------

| ✔ OpenAPI 3.0 Compliant
| ✔ Uses ``pydantic`` for schema objects
| ✔ Convert Serializers to schema objects
| ✔ All HTTP methods supported
| ✔ Built-in Views for viewing generated docs
| ✔ Granular customization when documenting individual Views


**Schema Driven Development** - Use ``pydantic`` to generate schema objects to document your Views. Your schemas can in turn be used to validate your requests and responses to ensure that they are consistent with your documentation.





Quickstart
----------