from unittest.mock import Mock
from pygls.types import (CompletionParams, Position,
                         TextDocumentIdentifier)
from pygls.workspace import Document, Workspace


from lark_language_server import server


class FakeServer():
    def __init__(self):
        self.workspace = Workspace('', None)


fake_document_uri = 'file://fake_doc.txt'
fake_document_content = 'text'
fake_document = Document(fake_document_uri, fake_document_content)


fake_server = FakeServer()
fake_server.show_message_log = Mock()
fake_server.workspace.get_document = Mock(return_value=fake_document)


def test_completions():
    """An example test which does very little"""
    completion_list = server.completions(
        fake_server,
        CompletionParams(TextDocumentIdentifier('file://fake_doc.txt'), Position(0, 2), None))
    # test the list is empty for now
    assert completion_list.items == []
