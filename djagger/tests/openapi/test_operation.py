from ...openapi import Operation, ExternalDocs, Server
from ...enums import HttpMethod

def test_extract_summary():

    # 1. No attribute
    class View:
        ...
    operation = Operation()
    operation._extract_summary(View, HttpMethod.GET)

    assert operation.summary == 'View' #View.__name__

    # 2. Use API-level attribute
    class View:
        summary='value1'
    
    operation = Operation()
    operation._extract_summary(View, HttpMethod.GET)

    assert operation.summary == View.summary

    # 3. Use operation-level attribute as priority
    class View:
        get_summary = 'value1'
        summary='value2'

    operation = Operation()
    operation._extract_summary(View, HttpMethod.GET)

    assert operation.summary == View.get_summary


def test_extract_description():

    # 1. No attribute
    class View:
        """This is the View docstring"""
        ...
    operation = Operation()
    operation._extract_description(View, HttpMethod.GET)

    assert operation.description == View.__doc__ 

    # 2. Use API-level attribute
    class View:
        description='value1'
    
    operation = Operation()
    operation._extract_description(View, HttpMethod.GET)

    assert operation.description == View.description

    # 3. Use operation-level attribute as priority
    class View:
        get_description = 'value1'
        description='value2'

    operation = Operation()
    operation._extract_description(View, HttpMethod.GET)

    assert operation.description == View.get_description

def test_extract_operation_id():

    # 1. No attribute
    class View:
        ...
    operation = Operation()
    operation._extract_operation_id(View, HttpMethod.GET)

    assert operation.operationId == None

    # 2. Use API-level attribute
    class View:
        operation_id='value1'
    
    operation = Operation()
    operation._extract_operation_id(View, HttpMethod.GET)

    assert operation.operationId == View.operation_id

    # 3. Use operation-level attribute as priority
    class View:
        get_operation_id = 'value1'
        operation_id='value2'

    operation = Operation()
    operation._extract_operation_id(View, HttpMethod.GET)

    assert operation.operationId == View.get_operation_id

def test_extract_deprecated():

    # 1. No attribute
    class View:
        ...
    operation = Operation()
    operation._extract_deprecated(View, HttpMethod.GET)

    assert operation.deprecated == None

    # 2. Use API-level attribute
    class View:
        deprecated=True
    
    operation = Operation()
    operation._extract_deprecated(View, HttpMethod.GET)

    assert operation.deprecated == View.deprecated

    # 3. Use operation-level attribute as priority
    class View:
        get_deprecated = True
        deprecated = False

    operation = Operation()
    operation._extract_deprecated(View, HttpMethod.GET)

    assert operation.deprecated == View.get_deprecated

def test_extract_tags():

    # 1. No attribute
    class View:
        ...
    operation = Operation()
    operation._extract_tags(View, HttpMethod.GET)

    assert operation.tags == [View.__module__.split(".")[0]]

    # 2. Use API-level attribute
    class View:
        tags=['app1', 'app2']
    
    operation = Operation()
    operation._extract_tags(View, HttpMethod.POST)
    assert operation.tags == View.tags

    # 3. Use API-level attribute
    class View:
        tags=['app3', 'app4']
        post_tags=['app1', 'app2']
    
    operation = Operation()
    operation._extract_tags(View, HttpMethod.POST)
    assert operation.tags == View.post_tags

def test_extract_external_docs():

    # 1. No attribute
    class View:
        ...
    operation = Operation()
    operation._extract_external_docs(View, HttpMethod.GET)

    assert operation.externalDocs == None

    # 2. Use API-level attribute
    class View:
        external_docs = {
            'url':'https://example.org'
        }
    
    operation = Operation()
    operation._extract_external_docs(View, HttpMethod.POST)
    assert operation.externalDocs == ExternalDocs.parse_obj(View.external_docs)


    # 3. Use operation-level attribute
    class View:
        external_docs = {
            'url':'https://example.org'
        }
        post_external_docs = {
            'url':'https://test.org'
        }
    
    operation = Operation()
    operation._extract_external_docs(View, HttpMethod.POST)
    assert operation.externalDocs.url == ExternalDocs.parse_obj(View.post_external_docs).url

def test_extract_servers():

    # 1. No attribute
    class View:
        ...
    operation = Operation()
    operation._extract_servers(View, HttpMethod.GET)

    assert operation.servers == None

    # 2. Use API-level attribute
    class View:
        servers = [{
            'url':'https://example.org'
        }]
    
    operation = Operation()
    operation._extract_servers(View, HttpMethod.POST)
    assert operation.servers == [ Server.parse_obj(server) for server in View.servers ]

    # 3. Use operation-level attribute
    class View:
        servers = [{
            'url':'https://example.org'
        }]
        post_servers = [{
            'url':'https://test.org'
        }]
    
    operation = Operation()
    operation._extract_servers(View, HttpMethod.POST)
    assert operation.servers == [ Server.parse_obj(server) for server in View.post_servers ]


def test_extract_security():

    # 1. No attribute
    class View:
        ...
    operation = Operation()
    operation._extract_security(View, HttpMethod.GET)

    assert operation.servers == None

    # 2. Use API-level attribute
    class View:
        security = [{
            'security1':['value1', 'value2']
        }]
    
    operation = Operation()
    operation._extract_security(View, HttpMethod.POST)
    assert operation.security == View.security

    # 3. Use operation-level attribute
    class View:
        security = [{
            'security1':['value1', 'value2']
        }]
        post_security = [{
            'security2':['value3', 'value4']
        }]

    operation = Operation()
    operation._extract_security(View, HttpMethod.POST)
    assert operation.security == View.post_security