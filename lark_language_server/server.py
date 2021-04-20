import typing as t
from pygls.lsp.methods import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                               TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN)
from pygls.server import LanguageServer
from pygls.lsp import (CompletionItem, CompletionList, CompletionParams,
                       CompletionOptions,
                       DidChangeTextDocumentParams,
                       DidCloseTextDocumentParams, DidOpenTextDocumentParams)

from .error_reporting import get_diagnostics


class LarkLanguageServer(LanguageServer):
    CONFIGURATION_SECTION = 'larkLanguageServer'

    def __init__(self):
        super().__init__()


lark_server = LarkLanguageServer()


def _validate(ls: LarkLanguageServer, params: DidChangeTextDocumentParams):
    ls.show_message_log('Validating document...')
    text_doc = ls.workspace.get_document(params.textDocument.uri)
    ls.publish_diagnostics(text_doc.uri, get_diagnostics(text_doc.source))


@lark_server.feature(COMPLETION, CompletionOptions(trigger_characters=[',']))
def completions(ls: LarkLanguageServer, params: CompletionParams = None):
    """Returns completion items."""
    ls.show_message_log('completion called @ {}'.format(params.position))
    items: t.List[CompletionItem] = []
    return CompletionList(is_incomplete=False, items=items)


@lark_server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LarkLanguageServer, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    # revalidate on every change
    _validate(ls, params)


@lark_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls: LarkLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    ls.show_message('Text Document Did Close')


@lark_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: LarkLanguageServer, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message('Text Document Did Open')
    _validate(ls, params)
