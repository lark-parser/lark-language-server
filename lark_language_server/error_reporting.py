from typing import List, Union
import logging
from lark import UnexpectedToken
from pygls.lsp import (Diagnostic, Range, Position)

from .lark_grammar import lark_grammar_parser


def user_repr(error: Union[UnexpectedToken]):
    if isinstance(error, UnexpectedToken):
        expected = ', '.join(error.accepts or error.expected)
        return f"Unexpected token {str(error.token)!r}. Expected one of:\n{{{expected}}}"
    else:
        return str(error)


def get_diagnostics(doctext: str):
    diagnostics: List[Diagnostic] = []

    def on_error(e: UnexpectedToken):
        diagnostics.append(Diagnostic(
            Range(
                Position(e.line - 1, e.column - 1),
                Position(e.line - 1, e.column)
            ),
            user_repr(e)))
        return True

    try:
        lark_grammar_parser.parse(doctext, on_error=on_error)
    except Exception:
        logging.exception("parser raised exception")
    return diagnostics
