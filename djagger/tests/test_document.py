def test_document():

    from ..openapi import Document

    document = Document.generate()
    assert document
