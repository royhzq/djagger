from ..schema import (
    DjaggerInfo, DjaggerLogo, DjaggerExternalDocs, DjaggerTag,
    DjaggerContact, DjaggerLicense
)

def test_djagger_logo():
    data = DjaggerLogo(
        url="https://example.org/image.png", 
        altText="Test logo image"
    ).dict()

    assert data


def test_djagger_external_docs():
    data = DjaggerExternalDocs(
        description="test description",
        url="URL of description"
    ).dict()
    assert data


def test_djagger_tag():
    data = DjaggerTag(
        name="Tag name",
        description = "description",
        externalDocs = DjaggerExternalDocs(
            description="test description",
            url="URL description"
        )
    ).dict()
    assert data

def test_djagger_contact():
    data = DjaggerContact(
        name="Test Name",
        url="Test URL",
        email="example@example.org"
    ).dict()
    assert data

def test_djagger_license():
    data = DjaggerLicense(
        name="test license name",
        url="license Url"
    ).dict()
    assert data


def test_djagger_info():

    data = DjaggerInfo(
        description = "Test Info Description",
        version = "2.0",
        title = "Test Djagger Info",
        termsOfService = "Reference to ToS",
        contact = DjaggerContact(),
        x_logo=DjaggerLogo(),
    ).dict(by_alias=True)
    assert data
    assert data.get('x-logo')