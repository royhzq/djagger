User Guide
==========

How It Works
------------
Under the hood, Djagger inspects the URLConf (URL configuration) of your Django project to obtain a manifest of all the views to document. Djagger proceeds to extract schema information from specific class (or function) attributes from these views. As the user, you configure the documentation by configuring these attributes in your views.

Request Parameters
------------------

Path, Query, Header, Cookie
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following parameters can be documented for API requests:

* **path** - Where the parameter value is part of the URL. E.g. ``/article/<int:pk>`` where ``pk`` is the path parameter. Document using ``path_params`` or ``<http_method>_path_params`` attribute in the view.
* **query** - Parameters that are appended to the URL. E.g. ``/articles?page=3`` where ``page`` is the query parameter. Document using ``query_params`` or ``<http_method>_query_params`` attribute in the view.
* **header** - Custom headers that are expected as part of the request. Document using ``header_params`` or ``<http_method>_header_params`` attribute in the view.
* **cookie** - Cookie value specific the API. Document using ``cookie_params`` or ``<http_method>_cookie_params`` attribute in the view.
* **request body** - HTTP body Data sent to the API commonly used for POST, PUT, UPDATE methods. Document using ``body_params`` or ``<http_method>_body_params`` attribute in the view.

Documenting path, query and cookie parameters:

.. code:: python

    from pydantic import BaseModel as Schema, Field
    from rest_framework.views import APIView
    from rest_framework.response import Response


    class ArticleYearSchema(Schema):
        year : int = Field(required=True)

    class ArticlePageSchema(Schema):
        page : int

    class ArticleHeaderSchema(Schema):
        api_key : str

    class ArticleCookieSchema(Schema):
        username : str


    class ArticlesYearAPI(APIView):

        """List all articles given a year"""

        path_params = ArticleYearSchema
        query_params = ArticlePageSchema
        header_params = ArticleHeaderSchema
        cookie_params = ArticleCookieSchema

        def get(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="" target="_blank">here</a>, and the code <a href="" target="_blank">here</a>.</p>

Request Body
~~~~~~~~~~~~
Document request body with ``body_params`` or ``<http_method>_body_params``.

.. code:: python


    class ArticleDeleteSchema(Schema):

        pk : int = Field(description="Primary key of article to delete")


    class ArticleDeleteAPI(APIView):

        body_params = ArticleDeleteSchema

        def delete(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="" target="_blank">here</a>, and the code <a href="" target="_blank">here</a>.</p>


By default, the media type documented is ``application/json`` if a pydantic model or a DRF serializer is passed as the value for ``body_params``. To customize for multiple media types or to change the default media type, pass in a dictionary with the string media type value as the key and the schema  (pydantic model / DRF serializer) as the value. 

.. code:: python

    ...

    class ToyUploadImageSchema(Schema):
        """Example values are not available for application/octet-stream media types."""
        ...
        __root__ : bytes


    class UploadImageAPI(APIView):

        summary = "Uploads an image"
        path_params = ToyIdSchema
        query_params = ToyMetaDataSchema
        body_params = {
            "application/octet-stream": ToyUploadImageSchema
        }
        response_schema = ToyUploadImageSuccessSchema

        def post(self, request, toyId: int):
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="" target="_blank">here</a>, and the code <a href="" target="_blank">here</a>.</p>


Response Objects
----------------

Single Response
~~~~~~~~~~~~~~~

Response objects are documented using the attribute ``response_schema`` or ``<http_method>_response_schema``. By default, if aa pydantic model or a DRF serializer class is passed as the value, the response is documented by default as a successful one i.e. 200 status code.

.. code:: python

    from pydantic import BaseModel as Schema, Field
    from rest_framework.views import APIView
    from rest_framework.response import Response
    import datetime


    class ArticleCreateSchema(Schema):
        """POST schema for blog article creation"""
        title : str = Field(description="Title of Blog article")
        content : str = Field(description="Blog article content")

    class ArticleDetailSchema(Schema):
        created : datetime.datetime
        title : str
        author : str
        content : str


    class ArticleCreateAPI(APIView):

        body_params = ArticleCreateSchema
        response_schema = ArticleDetailSchema

        def post(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="" target="_blank">here</a>, and the code <a href="" target="_blank">here</a>.</p>


Multiple Responses
~~~~~~~~~~~~~~~~~~

For multiple responses, or to change the default response, you may pass in a dictionary to ``response_schema`` with HTTP status code as a key and a pydantic model or DRF serializer as the value. 

.. code:: python

    class Login(APIView):

        summary = "Logs user into the system"
        query_params = LoginRequestSchema
        response_schema = {
            "200":LoginSuccessSchema,
            "400":LoginErrorSchema
        }

        def get(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="" target="_blank">here</a>, and the code <a href="" target="_blank">here</a>.</p>


Response Headers
~~~~~~~~~~~~~~~~

To document response headers, add ``headers`` to the ``Config`` class in the pydantic model schema. The value should be a dictionary with the header value as key and a Header object as the value. Refer the OpenAPI 3 docs for more information on the Header object specification.

.. code:: python

    from pydantic import BaseModel as Schema

    class LoginSuccessSchema(Schema):

        __root__ : str

        class Config:
            headers = {
                "X-Rate-Limit":{
                    "description":"calls per hour allowed by the user",
                    "type":"integer",
                    "schema":{
                        "type":"integer"
                    }
                },
                "X-Expires-After":{
                    "description":"date in UTC when token expires",
                    "type":"string",
                    "schema":{
                        "type":"strings"
                    }
                }
            }

.. raw:: html 

    <p>See the generated docs for this example <a href="" target="_blank">here</a>, and the code <a href="" target="_blank">here</a>.</p>


Schema Examples
----------------

To set examples for the schemas, define a classmethod ``example`` in the pydantic Schema model that returns an instance of itself with specific values. Defining examples this way has the added benefit of your examples being validated by the schema itself.
Examples defined this way only apply to documenting request bodies and responses i.e. ``body_params`` and ``response_schema``.

.. code:: python

    from pydantic import BaseModel as Schema
    from rest_framework.views import APIView


    class UserSchema(Schema):
        """A User object"""
        id : int
        username : str
        firstName : str
        lastName : str
        email : str
        password : str
        phone : str
        userStatus : int

        @classmethod
        def example(cls):
            return cls(
                id=10,
                username="theUser",
                firstName="John",
                lastName="James",
                email="john@email.com",
                password="12345",
                phone="12345",
                userStatus=4
            )

    class CreateUserAPI(APIView):
        """This can only be done by the logged in user."""

        summary = "Create user"
        body_params = UserSchema
        response_schema = UserSchema

        def post(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="" target="_blank">here</a>, and the code <a href="" target="_blank">here</a>.</p>

Defining examples for path, query, header and cookie parameters are done within the ``Field`` itself. For example:

.. code:: python

    from pydantic import BaseModel as Schema, Field

    class ArticleYearSchema(Schema):
        year : int = Field(required=True, example="2009")



Advanced Schemas
----------------
All ``Schema`` objects here are simply aliases of the pydantic ``BaseModel``. So all features of a pydantic model object can be utilized to define your schemas.

Nested Schemas
~~~~~~~~~~~~~~

To document nested schemas, you may use pydantic models as field types. This allows complex schemas to be managed easily and its components reusable.

.. code:: python

    from pydantic import BaseModel as Schema, Field
    from typing import List, Optional
    from enum import Enum


    class Status(str, Enum):
        available = 'available'
        pending = 'pending'
        sold = 'sold'

    class Category(Schema):
        """Toy Category"""
        id : int
        name : str

    class Tag(Schema):
        """Toy Tag"""
        id : int
        name : str

    class ToySchema(Schema):
        """Toy Schema"""
        id : Optional[int]
        name : str
        category : Optional[Category]
        photoUrls : List[str]
        tags : Optional[List[Tag]]
        status : Optional[Status] = Status.available
        ...


.. raw:: html 

    <p>See the generated docs for this example <a href="" target="_blank">here</a>, and the code <a href="" target="_blank">here</a>.</p>


Non-object Schemas
~~~~~~~~~~~~~~~~~~

By default, ``Schema`` objects will be documented as a JSON *object* i.e. an unordered set of name/value pairs. 
To change this, for example, if your API returns an array instead, change the ``__root__`` value of the ``Schema``.
Following from the example above:  

.. code:: python

    class ToyArraySchema(Schema):
        """An array of Toys""" 
        __root__: List[ToySchema]

    ...

    class FindToyByStatusAPI(APIView):
        """ Find Toys by status"""

        summary = "Find Toys by status"
        query_params = StatusSchema
        response_schema = {
            "200":ToyArraySchema,
            "400":InvalidToySchema
        }

        def get(self, request):
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="" target="_blank">here</a>, and the code <a href="" target="_blank">here</a>.</p>


API route Information
~~~~~~~~~~~~~~~~~~~~~
API method Information
~~~~~~~~~~~~~~~~~~~~~~

List of Djagger View attributes
-------------------------------

Document Generation
-------------------

Customizing Document Info
~~~~~~~~~~~~~~~~~~~~~~~~~




