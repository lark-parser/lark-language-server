import typing as t
from pygls.features import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                            TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN, WORKSPACE_DID_CHANGE_WATCHED_FILES)
from pygls.server import LanguageServer
from pygls.types import (CompletionItem, CompletionList, CompletionParams,
                         DidChangeTextDocumentParams,
                         DidCloseTextDocumentParams, DidOpenTextDocumentParams, DidChangeWatchedFiles)

from .error_reporting import get_diagnostics


class LarkLanguageServer(LanguageServer):
    CONFIGURATION_SECTION = 'larkLanguageServer'

    def __init__(self):
        super().__init__()


lark_server = LarkLanguageServer()


def _validate(ls: LarkLanguageServer, uri: str):
    ls.show_message_log('Validating document...')
    text_doc = ls.workspace.get_document(uri)
    ls.publish_diagnostics(text_doc.uri, get_diagnostics(text_doc.source))


@lark_server.feature(COMPLETION, trigger_characters=[','])
def completions(ls: LarkLanguageServer, params: CompletionParams = None):
    """Returns completion items."""
    ls.show_message_log('completion called @ {}'.format(params.position))
    items: t.List[CompletionItem] = []
    return CompletionList(False, items)


@lark_server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LarkLanguageServer, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    # revalidate on every change
    _validate(ls, params.textDocument.uri)

@lark_server.feature(WORKSPACE_DID_CHANGE_WATCHED_FILES)
def did_change(ls: LarkLanguageServer, params: DidChangeWatchedFiles):
    """Text document did change notification."""
    # revalidate on every change
    for e in params.changes:
        _validate(ls, e.uri)


@lark_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls: LarkLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    ls.show_message('Text Document Did Close')


@lark_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: LarkLanguageServer, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    print('Text Document Did Open')
    ls.show_message(f'Text Document Did Open {params.textDocument.uri}')
    _validate(ls, params.textDocument.uri)
