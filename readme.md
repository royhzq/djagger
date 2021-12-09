# Djagger 
Hassle-free, comprehensive automated OpenAPI document generator for Django.

## Quickstart

1. Add "djagger" to your INSTALLED_APPS setting like this:
```
    INSTALLED_APPS = [
        ...
        'djagger',
    ]
```  

2. Include the polls URLconf in your project urls.py like this:
```
    path('djagger/', include('djagger.urls')),
```