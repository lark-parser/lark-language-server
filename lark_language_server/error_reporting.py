from typing import List
from lark import UnexpectedToken
from pygls.types import (Diagnostic, Range, Position)

from .lark_grammar import lark_grammar_parser


def get_diagnostics(doctext: str):
    diagnostics: List[Diagnostic] = []

    def on_error(e: UnexpectedToken):
        diagnostics.append(Diagnostic(
            Range(
                Position(e.line - 1, e.column - 1),
                Position(e.line - 1, e.column)
            ),
            "unexpected input"))
        return True

    try:
        lark_grammar_parser.parse(doctext, on_error=on_error)
    except Exception as e:
        print(e)
    return diagnostics
