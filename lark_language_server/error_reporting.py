from typing import List, Union
import logging
from lark import UnexpectedToken, Token
from pygls.types import (Diagnostic, Range, Position)

from .lark_grammar import lark_grammar_parser


def user_repr(error: Union[UnexpectedToken]):
    if isinstance(error, UnexpectedToken):
        expected = ', '.join(error.accepts or error.expected)
        return f"Unexpected token {str(error.token)!r}. Expected one of:\n{{{expected}}}"
    else:
        return str(error)

_SOLUTIONS = {
    frozenset({'COLON', 'LBRACE', 'DOT'}): 'COLON',
    frozenset({'RULE'}): 'RULE',
    frozenset({'RPAR'}): 'RPAR',
    frozenset({'RSQB'}): 'RSQB',
}


def get_diagnostics(doctext: str):
    diagnostics: List[Diagnostic] = []

    def on_error(e: UnexpectedToken):
        t = e.token
        diagnostics.append(Diagnostic(
            Range(
                Position(t.line - 1, t.column - 1),
                Position(t.end_line - 1, t.end_column - 1)
            ),
            user_repr(e)))
        if t.type == '_NL': # Try to save ourself from overreporting errors
            logging.info(repr((t, t.line, t.end_line, t.column, t.end_column)))
            accepts = e.puppet.accepts()
            while frozenset(accepts) in _SOLUTIONS:
                tt = _SOLUTIONS[frozenset(accepts)]
                nt = Token.new_borrow_pos(tt, '<fill_token>', t)
                e.puppet.feed_token(nt)
                accepts = e.puppet.accepts()
            if '_NL' not in accepts:
                logging.warning('Unknown error situation with accepts: ' + str(accepts))
            e.puppet.feed_token(t)
        return True

    try:
        lark_grammar_parser.parse(doctext, on_error=on_error)
    except Exception:
        logging.exception("parser raised exception")
    return diagnostics
