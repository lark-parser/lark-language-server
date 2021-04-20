from unittest.mock import Mock
from pygls.lsp import (CompletionParams, Position,
                       TextDocumentIdentifier)
from pygls.workspace import Document, Workspace


from lark_language_server import server


class FakeServer():
    def __init__(self):
        self.workspace = Workspace('', None)
        self.show_message_log = Mock()
        self.workspace.get_document = Mock(return_value=fake_document)


fake_document_uri = 'file://fake_doc.txt'
fake_document_content = 'text'
fake_document = Document(fake_document_uri, fake_document_content)

fake_server = FakeServer()


def test_completions():
    """An example test which does very little"""
    completion_list = server.completions(
        fake_server,
        CompletionParams(
            text_document=TextDocumentIdentifier(uri='file://fake_doc.txt'),
            position=Position(line=0, character=2)))
    # test the list is empty for now
    assert completion_list.items == []
