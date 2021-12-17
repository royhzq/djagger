from ...swagger import (
    Info, 
    Logo, 
    Contact, 
    License,
)

def test_djagger_logo():
    data = Logo(
        url="https://example.org/image.png", 
        altText="Test logo image"
    ).dict()

    assert data

def test_djagger_contact():
    data = Contact(
        name="Test Name",
        url="Test URL",
        email="example@example.org"
    ).dict()
    assert data

def test_djagger_license():
    data = License(
        name="test license name",
        url="license Url"
    ).dict()
    assert data

def test_djagger_info():

    data = Info(
        description = "Test Info Description",
        version = "2.0",
        title = "Test Djagger Info",
        termsOfService = "Reference to ToS",
        contact = Contact(),
        x_logo=Logo(),
    ).dict(by_alias=True)
    assert data
    assert data.get('x-logo')