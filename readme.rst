===============================================================
🗡️Djagger - OpenAPI schema generator for Django using pydantic
===============================================================

.. |Package Badge| image:: https://github.com/royhzq/djagger/actions/workflows/python-package.yml/badge.svg
.. |Pypi Badge| image:: https://badge.fury.io/py/djagger.svg

|Package Badge| |Pypi Badge|


Automated OpenAPI documentation generator for Django. Djagger provides you with a clean and straightforward way to generate a comprehensive API documentation of your Django project by utilizing pydantic to create schema objects for your views.  

| Example Django project using Djagger: 
| https://github.com/royhzq/djagger-example
|
| Generated API documentation from the example project: 
| https://djagger-example.netlify.app/  
|
| The Djagger repo: 
| https://github.com/royhzq/djagger  
|
| Documentation:
| https://djagger-docs.netlify.app/index.html
| 

**Djagger is designed to be:**


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

.. image:: https://user-images.githubusercontent.com/32057276/148027310-3248b5aa-f8a5-46d1-b044-044d001dcddd.png
  :width: 800
  :alt: UserDetailsAPI Redoc
  :target: https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1articles~1random/get
  
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

.. image:: https://user-images.githubusercontent.com/32057276/148027403-4acca98c-e4af-4265-a9f5-c385f143be73.png
  :width: 800
  :alt: CreateItemAPI Redoc
  :target: https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1articles~1create/post
  

Documentation & Support
=======================
* This project is in continuous development. If you have any questions or would like to contribute, please email `royhung@protonmail.com <royhung@protonmail.com>`_
* If you want to support this project, do give it a ⭐ on github!
