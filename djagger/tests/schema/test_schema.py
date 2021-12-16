""" Tests for base document generation i.e., ``DjaggerDoc`` class
"""

from ...schema import (
    DjaggerExternalDocs, 
    DjaggerTag,
)

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