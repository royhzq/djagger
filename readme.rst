=========
🗡️Djagger
=========

.. |Package Badge| image:: https://github.com/royhzq/djagger/actions/workflows/python-package.yml/badge.svg
.. |Pypi Badge| image:: https://badge.fury.io/py/djagger.svg

|Package Badge| |Pypi Badge|


Automated OpenAPI documentation generator for Django. Djagger helps you generate a complete and comprehensive API documentation of your Django project by utilizing pydantic to create schema objects for your views.  

Djagger is designed to be:

🧾 **Comprehensive** - ALL aspects of your API should be document-able straight from your views, to the full extent of the OpenAPi 3.0 specification. 


👐 **Unintrusive** - Integrate easily with your existing Django project. Djagger can document vanilla Django views (function-based and class-based views), as well as any Django REST framework views. As long as you are using Django's default URL routing, you are good to go. You do not need to redesign your APIs for better documentation.


🍭 **Easy** - Djagger uses pure, unadulterated pydantic models to generate schemas. If you have used pydantic, there is no learning curve. If you have not heard of pydantic, it is a powerful data validation library that is pretty straightforward to pickup (like dataclasses). `Check it out here <https://pydantic-docs.helpmanual.io/>`_. Either way, documenting your APIs will feel less like a chore.



Quick start
-----------

Install using ``pip``

.. code:: bash

    pip install djagger



Add 'djagger' to your ``INSTALLED_APPS`` setting like this

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
    

| ⭐To see the generated documentation, use the route **/djagger/api/docs**. Djagger uses `Redoc <https://github.com/Redocly/redoc>`_ as the default client generator.
⭐To get the generated JSON schema file, use the route **/djagger/schema.json**.  


Note that the path ``djagger/`` is required when setting this URLconf.  Feel free to remove ``djagger.urls`` when you are more comfortable and decide to customize your own documentation views. The routes provided here are for you to get started quickly.



Examples
--------

In the examples, we alias pydantic ``BaseModel`` as ``Schema`` to avoid any confusion with Django's `Model` ORM objects. Django REST Framework views are used for the examples.  

Example GET Endpoint
====================

.. code:: python

    from rest_framework.views import APIView
    from rest_framework.response import Response
    
    from pydantic import BaseModel as Schema

    class UserDetailsParams(Schema):

        pk : int

    class UserDetailsResponse(Schema):
        """ GET response schema for user details
        """
        first_name : str
        last_name : str
        age : int
        email: str

    class UserDetailsAPI(APIView):

        """ Lists a given user's details. 
        Docstrings here will be used for the API's description in
        the generated schema.
        """

        get_path_params = UserDetailsParams
        get_response_schema = UserDetailsResponse   

        def get(self, request, pk : int):

            return Response({
                "first_name":"John", 
                "last_name":"Doe",
                "age": 30,
                "email":"john_doe@example.org"
            })

**Generated documentation**

.. image:: https://user-images.githubusercontent.com/32057276/145702881-29531b7e-7059-406e-b1cb-54d58fcb6900.PNG
  :width: 800
  :alt: UserDetailsAPI Redoc
  
Example POST Endpoint
=====================

.. code:: python

    from pydantic import BaseModel as Schema, Field
    from typing import Optional
    from decimal import Decimal

    class CreateItemRequest(Schema):
        """ POST request body schema for creating an item.
        """
        sku : str = Field(description="Unique identifier for an item")
        name : str = Field(description="Name of an item")
        price : Decimal = Field(description="Price of item in USD")
        min_qty : int = 1
        description : Optional[str]

    class CreateItemResponse(Schema):
        """ Post response schema for successful item creation.
        """
        pk : int 
        details : str = Field(description="Details for the user")

    class CreateItemAPI(APIView):

        """ Endpoint to create an item.
        """

        summary = "Create Item API Title" # Change title of API
        post_body_params = CreateItemRequest
        post_response_schema = CreateItemResponse   

        def post(self, request):

            # Some code here...

            return Response({
                "pk":1,
                "details":"Successfully created item."
            })

**Generated documentation**

.. image:: https://user-images.githubusercontent.com/32057276/145703400-1bd56954-5ae7-4f5a-a1ad-560fde824880.PNG
  :width: 800
  :alt: CreateItemAPI Redoc
  
To include multiple responses for the above endpoint, for example, an error response code, create a new ``Schema`` for the error response and change the ``post_response_schema`` attribute to the following 

.. code:: python

    class ErrorResponse(Schema):
        """ Response schema for errors. 
        """
        status_code : int 
        details : str = Field(description="Error details for the user")

    class CreateItemAPI(APIView):

        """ API View to create an item.
        """

        summary = "Create Item API Title" # Change title of API
        post_body_params = CreateItemRequest
        post_response_schema = {
            "200": CreateItemResponse,
            "400": ErrorResponse
        }

        def post(self, request):
            ...

**Generated documentation**

.. image:: https://user-images.githubusercontent.com/32057276/145703917-9fc5ef8e-5591-4e26-a94a-6d20c89e0836.PNG
  :width: 800
  :alt: ErrorResponse Redoc


Documentation & Support
-----------------------
* Full documentation is currently a work in progress.
* This project is in continuous development. If you have any questions or would like to contribute, please email `royhung@protonmail.com <royhung@protonmail.com>`_
* If you want to support this project, do give it a ⭐ on github!
