""" Tests for base document generation i.e., ``Document`` class
"""

from ...swagger import (
    ExternalDocs, 
    Tag,
)

def test_djagger_external_docs():
    data = ExternalDocs(
        description="test description",
        url="URL of description"
    ).dict()
    assert data


def test_djagger_tag():
    data = Tag(
        name="Tag name",
        description = "description",
        externalDocs = ExternalDocs(
            description="test description",
            url="URL description"
        )
    ).dict()
    assert data