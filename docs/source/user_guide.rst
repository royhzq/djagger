User Guide
==========

How It Works
------------
Under the hood, Djagger inspects the URLConf (URL configuration) of your Django project to obtain a manifest of all the views to document. Djagger proceeds to extract schema information from specific class (or function) attributes from these views. As the user, you configure the documentation by configuring these attributes in your views.

The Schema Object
~~~~~~~~~~~~~~~~~

The ``Schema`` object is simply an alias of pydantic's ``pydantic.main.BaseModel`` class. This is to avoid confusion with Django models. From here on, this documentation will use the alias ``Schema`` but you may choose to go without an alias, or use another one in your own projects.

Thanks to pydantic, the ``Schema`` object is a clean and powerful tool to document your requests and responses. In djagger, the ``Schema`` object is used to document request parameters (headers, cookies, path, query), request bodies, and responses. 


.. code:: python

    from pydantic import BaseModel as Schema, Field

    class MyResponse(Schema):
        """This docstring will be used to describe the response"""
        name : str 
        age : int
        remarks : Optional[str]
        email : str = Field("default@example.com", description="This is a description of the field)

In the example above, a response for an API is documented as such. A few things to take note of:

* Docstrings will be extracted to describe the particular schema in the generated documentation. 
* For non-required fields, use ``Optional[]`` 
* For more information regarding the fields, use ``Field`` for setting things like default values, descriptions, min and max values etc. 

See `pydantic's documentation <https://pydantic-docs.helpmanual.io/>`_ for more details.

Request Parameters
------------------

Path, Query, Header, Cookie
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following parameters can be documented for API requests:

* **path** - Where the parameter value is part of the URL. E.g. ``/article/<int:pk>`` where ``pk`` is the path parameter. Document using ``path_params`` or ``<http_method>_path_params`` attribute in the view.
* **query** - Parameters that are appended to the URL. E.g. ``/articles?page=3`` where ``page`` is the query parameter. Document using ``query_params`` or ``<http_method>_query_params`` attribute in the view.
* **header** - Custom headers that are expected as part of the request. Document using ``header_params`` or ``<http_method>_header_params`` attribute in the view.
* **cookie** - Cookie value specific the API. Document using ``cookie_params`` or ``<http_method>_cookie_params`` attribute in the view.
* **request body** - HTTP body Data sent to the API commonly used for POST, PUT, UPDATE methods. Document using ``request_schema`` or ``<http_method>_request_schema`` attribute in the view.

Documenting path, query and cookie parameters:

.. code:: python

    from pydantic import BaseModel as Schema, Field
    from rest_framework.views import APIView
    from rest_framework.response import Response
    from .schema import ListArticleDetailSchema


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
        response_schema = ListArticleDetailSchema

        def get(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1articles~1{year}~1/get" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Blog/views.py#L72" target="_blank">here</a>.</p>

Request Body
~~~~~~~~~~~~
Document request body with ``request_schema`` or ``<http_method>_request_schema``.

.. code:: python

    from pydantic import BaseModel as Schema, Field
    from rest_framework.views import APIView

    class ArticleCreateSchema(Schema):
        """POST schema for blog article creation"""

        title: str = Field(description="Title of Blog article")
        content: str = Field(description="Blog article content")


    class ArticleCreateAPI(APIView):

        request_schema = ArticleCreateSchema
        ...

        def post(self, request):
            ...

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1articles~1create/post" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Blog/views.py#L45" target="_blank">here</a>.</p>


By default, the media type documented is ``application/json`` if a pydantic model or a DRF serializer is passed as the value for ``request_schema``. To customize for multiple media types or to change the default media type, pass in a dictionary with the string media type value as the key and the schema  (pydantic model / DRF serializer) as the value. 

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
        request_schema = {
            "application/octet-stream": ToyUploadImageSchema
        }
        response_schema = ToyUploadImageSuccessSchema

        def post(self, request, toyId: int):
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Toy/paths/~1toy~1{toyId}~1uploadImage/post" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Toy/views.py#L110" target="_blank">here</a>.</p>


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

        request_schema = ArticleCreateSchema
        response_schema = ArticleDetailSchema

        def post(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1articles~1create/post" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Blog/views.py#L45" target="_blank">here</a>.</p>


Multiple Responses
~~~~~~~~~~~~~~~~~~

For multiple responses, or to change the default response, you may pass in a dictionary to ``response_schema`` with HTTP status code as a key and a pydantic model or DRF serializer as the value. 

To customize the content type of the response, pass in a string tuple containing the status code and the content type as the key.

.. code:: python

    class Login(APIView):

        summary = "Logs user into the system"
        query_params = LoginRequestSchema
        response_schema = {
            "200":LoginSuccessSchema,
            "400":LoginErrorSchema,
            ("403", "text/plain"): ForbiddenSchema
        }

        def get(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/User/paths/~1user~1login/get" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/User/views.py#L38" target="_blank">here</a>.</p>


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

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/User/paths/~1user~1login/get" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/User/schemas.py#L56" target="_blank">here</a>.</p>


Schema Examples
----------------

To set examples for the schemas, define a classmethod ``example`` in the pydantic Schema model that returns an instance of itself with specific values. Defining examples this way has the added benefit of your examples being validated by the schema itself.
Examples defined this way only apply to documenting request bodies and responses i.e. ``request_schema`` and ``response_schema``.

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
        request_schema = UserSchema
        response_schema = UserSchema

        def post(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/User/paths/~1user~1/post" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/User/views.py#L16" target="_blank">here</a>.</p>

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

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Toy/paths/~1toy~1/post" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Toy/schemas.py#L20" target="_blank">here</a>.</p>


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

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Toy/paths/~1toy~1findByStatus/get" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Toy/views.py#L44" target="_blank">here</a>.</p>


List of Djagger View attributes
-------------------------------

The table below lists the attributes that can be defined in a view that will be extracted by Djagger to build the documentation.
For class-based views encompassing multiple HTTP methods, the attributes below will apply to ALL HTTP methods. 

To differentiate the attributes for different HTTP methods, prefix the method name in front of any of the attributes in the table below. For example, instead of declaring the class attribute ``response_schema``, you may declare both ``get_response_schema`` and ``post_response_schema`` to differentiate between GET and POST responses. See example below.

The available HTTP method names for the prefix are ``get``, ``post``, ``patch``, ``delete``, ``put``, ``options``, ``head``, ``trace``.


.. NOTE::
    **Hierarchy of Specificity** - A more specific declaration of a Djagger view attribute will override a less specific one. 
    For example, having both ``summary`` and ``post_summary`` attributes will result in the POST endpoint taking on the value of ``post_summary`` while the other endpoints will take on the summary value of ``summary`` in the documentation.


+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Attribute        | Type                                                                                  | Description                                                                                                                                                                                                                                                                                                           |
+==================+=======================================================================================+=======================================================================================================================================================================================================================================================================================================================+
| path_params      | pydantic.main.ModelMetaclass | rest_framework.serializers.SerializerMetaclass         | Schema for the parameter values that are part of the URL E.g. /article/<int:pk> where pk is the path parameter.                                                                                                                                                                                                       |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| query_params     | pydantic.main.ModelMetaclass | rest_framework.serializers.SerializerMetaclass         | Schema for the parameter values that are appended to the URL. E.g. /articles?page=3 where page is the query parameter.                                                                                                                                                                                                |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| header_params    | pydantic.main.ModelMetaclass | rest_framework.serializers.SerializerMetaclass         | Schema for custom headers that are expected as part of the request.                                                                                                                                                                                                                                                   |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| cookie_params    | pydantic.main.ModelMetaclass | rest_framework.serializers.SerializerMetaclass         | Schema for cookie values specific to the API.                                                                                                                                                                                                                                                                         |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| request_schema   | pydantic.main.ModelMetaclass | rest_framework.serializers.SerializerMetaclass | Dict  | Schema for HTTP body Data sent to the API commonly used for POST, PUT, UPDATE methods. Can accept a dictionary of string keys representing media types and values of ModelMetaclass or SerializerMetaclass.                                                                                                           |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| response_schema  | pydantic.main.ModelMetaclass | rest_framework.serializers.SerializerMetaclass | Dict  | Schema for responses returned by the API. By default, if aa pydantic model or a DRF serializer class is passed as the value, the response is documented by default as a successful one i.e. 200 status code. Can accept a dictionary of string HTTP status codes and values of ModelMetaclass or SerializerMetaclass  |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| summary          | str                                                                                   | Summary of the API. By default, the value used will be the __name__ value of the view if this attribute is not specified.                                                                                                                                                                                             |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| tags             | List[str]                                                                             | List of string tag names.                                                                                                                                                                                                                                                                                             |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| description      | str                                                                                   | String description of the API. By default, the docstrings of the view will be used if this attribute is not specified.                                                                                                                                                                                                |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| operation_id     | str                                                                                   | Unique string used to identify the operation                                                                                                                                                                                                                                                                          |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| deprecated       | bool                                                                                  | Boolean value to indicate if API is deprecated. Defaults to True                                                                                                                                                                                                                                                      |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| external_docs    | dict                                                                                  | Dictionary containing url and description fields to describe external documentation for the API.                                                                                                                                                                                                                      |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| servers          | List[dict]                                                                            | List of dictionary Server objects which provide connectivity information to a target server.                                                                                                                                                                                                                          |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| security         | List[dict]                                                                            | A declaration of which security mechanisms can be used across the API.                                                                                                                                                                                                                                                |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| djagger_exclude  | bool                                                                                  | Declare this attribute as True to skip documentation of the API.                                                                                                                                                                                                                                                      |
+------------------+---------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


**Example with HTTP method specific attributes**

.. code:: python
    
    ...

    class FindToyByIdAPI(APIView):

        get_summary = "Find Toy by ID"
        get_path_params = ToyIdSchema
        get_response_schema = {
            "200":ToySchema,
            "400":InvalidToySchema,
            "404":ToyNotFoundSchema
        }
        
        post_summary = "Update Toy with form data"
        post_request_schema = {
            "multipart/form-data":ToyIdFormSchema
        }
        post_response_schema = {
            "405":InvalidToySchema
        }

        delete_summary = "Deletes a Toy"
        delete_header_params = ToyDeleteHeaderSchema
        delete_path_params = ToyIdSchema
        delete_response_schema = {
            "400":InvalidToySchema
        }

        def get(self, request, toyId: int):
            ...
            return Response({})

        def post(self, request, toyId: int):
            ...
            return Response({})

        def delete(self, request, toyId: int):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Toy/paths/~1toy~1{toyId}/get" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Toy/views.py#L74" target="_blank">here</a>.</p>


Function-based Views
--------------------
Djagger supports documenting function-based views (FBV). For FBVs, add the decorator ``@schema`` to the view function. The decorator takes in a required ``methods`` list of string HTTP methods that indicate the HTTP methods handled by the view. Arguments can be passed based on the List of Djagger View attributes into the decorator, these arguments work in the same manner as the class attributes for class-based views.

.. code:: python

    from pydantic import BaseModel as Schema
    from djagger.decorators import schema
    from typing import List


    class AuthorSchema(Schema):
        first_name : str
        last_name : str

    class AuthorListSchema(Schema):
        authors : List[AuthorSchema] 


    @schema(
        methods=['GET', 'POST'],
        get_summary="List Authors",
        get_response_schema=AuthorListSchema,
        post_summary="Create Author",
        post_request_schema=AuthorSchema,
        post_response_schema=AuthorSchema,
    )
    def author_api(request):
        """API to create an author or list all authors"""

        if request.method == 'get':
            ...
            return Response({})

        if request.method == 'post':
            ...
            return Response({})


.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1author/get" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Blog/views.py#L85" target="_blank">here</a>.</p>


Using Serializers
-----------------

Wherever a pydantic model is used as a schema e.g. in documenting responses or request parameters, a Django REST Framework (DRF) Serializer object can also be used as an alternative. 

Under the hood, Djagger converts the serializer class (``rest_framework.serializers.SerializerMetaclass``) to a valid pydantic model (``pydantic.main.ModelMetaclass``).

For example:

.. code:: python

    from rest_framework import serializers
    from rest_framework.views import APIView
    from .schemas import ArticleDetailSchema


    class ArticleUpdateSerializer(serializers.Serializer):

        pk = serializers.IntegerField(help_text="Primary key of article to update")
        title = serializers.CharField(required=False)
        content = serializers.CharField(required=False)


    class ArticleUpdateAPI(APIView):

        request_schema = ArticleUpdateSerializer
        response_schema = ArticleDetailSchema
        
        def put(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1articles~1update/put" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Blog/views.py#L54" target="_blank">here</a>.</p>

Generic Views
-------------

For generic views, if a ``serializer_class`` attribute is defined for the generic view, Djagger will treat it as a ``response_schema`` attribute. Setting ``response_schema`` directly in the generic view will override this. Other than that, documenting generic views is the same as a regular class-based view.

.. code:: python

    class CategoryList(generics.ListCreateAPIView):
        """Example Generic View Documentation"""

        serializer_class = CategorySerializer(many=True)
        get_summary = "Category List"
        post_summary = "Category List Create"

        def list(self, request):
            ...
            return Response({})

        def create(self, request):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Blog/paths/~1blog~1categories~1/get" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Blog/views.py#L104" target="_blank">here</a>.</p>



Viewsets
--------

Documenting DRF viewsets is supported. To document each viewset action e.g. ``list()``, ``create()``, decorate the action method with the ``@schema`` decorator similar to how a function-based view is documented in Djagger. 

For viewsets, the parent viewset class attributes can also be used for documenting the actions, and they will apply to all actions under the viewset. The ``@schema`` values will take priority over the parent class djagger atributes.

.. code:: python

    class CategoryViewset(viewsets.ViewSet):
        """Example Viewset documentation"""
        
        response_schema = CategoryListSchema

        @schema(
            methods=['GET'],
            summary="List Categories",
        )
        def list(self, request):
            ...
            return Response({})

        @schema(
            methods=['GET'],
            summary="Get Category",
            response_schema=CategorySerializer,
        )
        def retrieve(self, retrieve):
            ...
            return Response({})

.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/#tag/Blog/paths/~1cat~1/get" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/7293a78388498ec6d9fc74c6b299bfc16374bf57/Blog/views.py#L119" target="_blank">here</a>.</p>


Tags
----
You can group APIs with tags. Tags are an OpenAPi 3 schema object and they can be declared using the ``tags`` djagger attribute. ``tags`` should be a list of string tag names for which the operation should be assigned to.

By default, djagger will create tags for each Django app included in the project, unless overwritten in the ``DJAGGER_DOCUMENT`` settings configuration. In your views, if ``tags`` attribute is not set, the API will be automatically assigned the tag name of the Django app in which it resides. 

.. NOTE::
    The http method prefix is also applicable to the ``tags`` attribute. So a view with ``tags=['MyApp']`` and ``post_tags=['Admin']``
    will have POST operations take on the ``Admin`` tag while other operations assigned the ``MyApp`` tag. 

**Example**

.. code:: python

    class MyView(APIView):

        tags = ['MyApp']
        post_tags = ['Admin']

        def get(self, request):
            # Assigned to 'MyApp' tag
            ...
            return Response({})

        def post(self, request):
            # Assigned to 'Admin' tag
            ...
            return Response({})

Defining tags at the document level
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define the tags at the document level in with the ``DJAGGER_DOCUMENT`` settings in ``settings.py``.
``tags`` key should be a list of tag dictionaries of type ``Dict[str,str]`` containing ``name`` and ``description`` keys.

**Example**

.. code:: python

    # settings.py

    DJAGGER_DOCUMENT = {
        ...
        "tags" : [
            { 'name':'Tag1', 'description': 'Example Tag'},
            { 'name':'Tag2', 'description': 'Example Tag'},
        ],
        ...
    }

Defining document-level tags in this way overrides the default tags created for each django app.


Document Generation
-------------------

To see the generated documentation, ensure that the Djagger URLs are installed correctly. See :ref:`getting_started:Getting Started`.


Configuring the built-in Djagger views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration for the built-in document view is managed in ``settings.py`` via the dictionary parameter ``DJAGGER_DOCUMENT``.
See table below for the valid dict keys in ``settings.DJAGGER_DOCUMENT``.

+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Keys              | Type       | Description                                                                                                                                                                                                                                |
+===================+============+============================================================================================================================================================================================================================================+
| app_names         | List[str]  | Required list of string names for the Django apps to be documented. Apps not included in this list will not be documented.                                                                                                                 |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| tags              | List[dict] | List of dictionary objects with name and description fields representing the OpenAPI Tag object. By default, the list of declared app names in DJAGGER_APP_NAMES will be created as the OpenAPI Tags, unless overridden by this variable.  |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| openapi           | str        | OpenAPI 3 version. Defaults to 3.0.0.                                                                                                                                                                                                      |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| version           | str        | Project version. Defaults to 1.0.0.                                                                                                                                                                                                        |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| servers           | List[dict] | List of dictionary Server objects. Each object is a dictionary with url and description string fields.                                                                                                                                     |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| security          | List[dict] | List of dictionary Security objects.                                                                                                                                                                                                       |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| title             | str        | Title of documentation.                                                                                                                                                                                                                    |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| description       | str        | Description of documentation.                                                                                                                                                                                                              |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| terms_of_service  | str        | Terms of service.                                                                                                                                                                                                                          |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| contact_name      | str        | Contact name.                                                                                                                                                                                                                              |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| contact_email     | str        | Contact email.                                                                                                                                                                                                                             |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| contact_url       | str        | Contact URL.                                                                                                                                                                                                                               |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| license_name      | str        | Name of license                                                                                                                                                                                                                            |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| license_url       | str        | URL of license                                                                                                                                                                                                                             |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| kwargs            |            | Additional key/value pairs to be appended to the generated JSON document. Usually used for ``x-`` fields for specific document generating clients.                                                                                         |
+-------------------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


**Example Djagger Document settings**

.. code:: python

    # settings.py 

    DJAGGER_DOCUMENT = {
        "version" : "1.0.0",
        "title" : "Djagger Toy Store",
        "description" : """This is a sample OpenAPI 3.0 schema generated from a Django project using Djagger. 

    View the Django project that generated this document on Github: https://github.com/royhzq/djagger-example.

        """,
        "license_name" : "MIT",
        "app_names" : [ 'Toy', 'Store', 'User', 'Blog'],
        "tags" : [
            { 'name':'Toy', 'description': 'Toy App'},
            { 'name':'Store', 'description': 'Store App'},
            { 'name':'User', 'description': 'User App'},
            { 'name':'Blog', 'description': 'Blog App'},
        ],
        "x-tagGroups" : [
            { 'name':'GENERAL', 'tags': ['Toy', 'Store', 'Blog']},
            { 'name':'USER MANAGEMENT', 'tags': ['User']}
        ],
        "servers" : [
            {
                "url":"https://example.org",
                "description":"Production API server"
            },
            {
                "url":"https://staging.example.org",
                "description":"Staging API server"
            }
        ],
    }
.. raw:: html 

    <p>See the generated docs for this example <a href="https://djagger-example.netlify.app/" target="_blank">here</a>, and the code <a href="https://github.com/royhzq/djagger-example/blob/285af0109155f6ef13e94302a0d40749501388cf/djagger_example/settings.py#L134" target="_blank">here</a>.</p>

Customized documentation views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create your own documentation view, generate the document via Djagger's ``Document`` class. See example below: 

.. code:: python

    from djagger.openapi import Document
    from django.http import JsonResponse

    def custom_doc_view(request):

        """ Custom documentation View for auto generated OpenAPI JSON document """

        doc_settings = {
            "version" : "1.0.0",
            "title" : "Djagger Toy Store",
            "description" : """This is a sample OpenAPI 3.0 schema generated from a Django project using Djagger. 

        View the Django project that generated this document on Github: https://github.com/royhzq/djagger-example.

            """,
            "license_name" : "MIT",
            "app_names" : [ 'Toy', 'Store', 'User', 'Blog'],
            "tags" : [
                { 'name':'Toy', 'description': 'Toy App'},
                { 'name':'Store', 'description': 'Store App'},
                { 'name':'User', 'description': 'User App'},
                { 'name':'Blog', 'description': 'Blog App'},
            ],
            "x-tagGroups" : [
                { 'name':'GENERAL', 'tags': ['Toy', 'Store', 'Blog']},
                { 'name':'USER MANAGEMENT', 'tags': ['User']}
            ],
            "servers" : [
                {
                    "url":"https://example.org",
                    "description":"Production API server"
                },
                {
                    "url":"https://staging.example.org",
                    "description":"Staging API server"
                }
            ],
        }

        document : dict = Document.generate(**doc_settings)

        response = JsonResponse(document)
        response['Cache-Control'] = "no-cache, no-store, must-revalidate"
        return response

The ``custom_doc_view`` view in the example returns a JSON response containing the OpenAPI 3 compliant JSON schema. You may then use your preferred documentation client generator to consume the JSON schema from the view to generate your desired documentation.


Global attribute prefix
-----------------------

In the event that certain djagger attributes come into conflict with those from other packages when used together in the same view, you can set a global prefix for all djagger attributes to overcome this. 

For example, a global prefix of ``dj_`` will mean that all djagger attributes will need to be prefixed as such for all class-based views as well as the parameters of the ``@schema`` function-based view decorator. I.e. Instead of ``get_summary``, the attribute will be ``dj_get_summary``.

To set the prefix, add the following in ``settings.py``

.. code:: python

    DJAGGER_CONFIG = {
        "global_prefix" = "dj_"
    }

With the prefix, an example of a documented view will be:

.. code:: python

    # Class-based view

    class TestView(APIView):

        dj_get_summary="Test View"
        dj_request_schema=...
        dj_response_schema=...
        

    # Function-based view

    @schema(
        dj_get_summary="Test View"
        dj_request_schema=...
        dj_response_schema=...
    )
    def fbv(request):
        ...







