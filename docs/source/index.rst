===============================================================
🗡️Djagger - OpenAPI schema generator for Django using pydantic
===============================================================

.. |Package Badge| image:: https://github.com/royhzq/djagger/actions/workflows/python-package.yml/badge.svg
.. |Pypi Badge| image:: https://badge.fury.io/py/djagger.svg

|Package Badge| |Pypi Badge|


Automated OpenAPI documentation generator for Django. Djagger provides you with a clean and straightforward way to generate a comprehensive API documentation of your Django project by utilizing pydantic to create schema objects for your views.  

| See a working example of a Django project using Djagger: 
| https://github.com/royhzq/djagger-example

| See the generated API documentation from the example project: 
| https://djagger-example.netlify.app/  

| The Djagger repo: 
| https://github.com/royhzq/djagger  


Djagger is designed to be:

🧾 **Comprehensive** - Every aspect of your API should be document-able straight from your views, to the full extent of the OpenAPi 3.0 specification. 


👐 **Unintrusive** - Integrate easily with your existing Django project. Djagger can document vanilla Django views (function-based and class-based views), as well as any Django REST framework views. As long as you are using Django's default URL routing, you are good to go. You do not need to redesign your APIs for better documentation.


🍭 **Easy** - Djagger uses pure, unadulterated pydantic models to generate schemas. If you have used pydantic, there is no learning curve. If you have not heard of pydantic, it is a powerful data validation library that is pretty straightforward to pickup (like dataclasses). `Check it out here <https://pydantic-docs.helpmanual.io/>`_. Either way, documenting your APIs will feel less like a chore.

Examples
--------

Example GET Endpoint
====================

.. code:: python

    from rest_framework.views import APIView
    from rest_framework.response import Response
    from pydantic import BaseModel as Schema
    import datetime


    class ArticleDetailSchema(Schema):
        created : datetime.datetime
        title : str
        author : str
        content : str


    class RandomArticleAPI(APIView):
        """Return a random article from the Blog"""

        response_schema = ArticleDetailSchema

        def get(self, request):
            ...
            return Response({})


**Generated documentation**

.. raw:: html 

    <p>See the generated docs <a href="https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1articles~1random/get" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/285af0109155f6ef13e94302a0d40749501388cf/Blog/views.py#L26" target="_blank">here</a>.</p>


.. image:: https://user-images.githubusercontent.com/32057276/145702881-29531b7e-7059-406e-b1cb-54d58fcb6900.PNG
  :width: 800
  :alt: UserDetailsAPI Redoc
  
Example POST Endpoint
=====================

.. code:: python

    from rest_framework.views import APIView
    from rest_framework.response import Response
    from pydantic import BaseModel as Schema, Field
    import datetime


    class ArticleDetailSchema(Schema):
        created : datetime.datetime
        title : str
        author : str
        content : str

    class ArticleCreateSchema(Schema):
        """POST schema for blog article creation"""
        title : str = Field(description="Title of Blog article")
        content : str = Field(description="Blog article content")


    class ArticleCreateAPI(APIView):

        request_schema = ArticleCreateSchema
        response_schema = ArticleDetailSchema

        def post(self, request):
            ...
            return Response({})




**Generated documentation**

.. raw:: html 

    <p>See the generated docs <a href="https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1articles~1create/post" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/285af0109155f6ef13e94302a0d40749501388cf/Blog/views.py#L45" target="_blank">here</a>.</p>

.. image:: https://user-images.githubusercontent.com/32057276/145703400-1bd56954-5ae7-4f5a-a1ad-560fde824880.PNG
  :width: 800
  :alt: CreateItemAPI Redoc
  

Documentation & Support
=======================
* This project is in continuous development. If you have any questions or would like to contribute, please email `royhung@protonmail.com <royhung@protonmail.com>`_
* If you want to support this project, do give it a ⭐ on github!



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   user_guide
   api
   release_history
   contributing
