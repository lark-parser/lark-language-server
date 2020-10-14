from typing import List, Union
import logging
from lark import UnexpectedToken, Token, UnexpectedCharacters
from pygls.types import Diagnostic, Range, Position
import re

from .lark_grammar import lark_grammar_parser


def user_repr(error: Union[UnexpectedToken]):
    if isinstance(error, UnexpectedToken):
        expected = ", ".join(error.accepts or error.expected)
        return f"Unexpected token {str(error.token)!r}. Expected one of:\n{{{expected}}}"
    else:
        return str(error)


_SOLUTIONS = {
    frozenset({"COLON", "LBRACE", "DOT"}): "COLON",
    frozenset({"RULE"}): "RULE",
    frozenset({"RPAR"}): "RPAR",
    frozenset({"RSQB"}): "RSQB",
}


def on_token_error(e: UnexpectedToken, diagnostics: List[Diagnostic]):
    t = e.token
    diagnostics.append(
        Diagnostic(
            Range(
                Position(t.line - 1, t.column - 1),
                Position(t.end_line - 1, t.end_column - 1),
            ),
            user_repr(e),
        )
    )
    if (
        t.type == "_NL"
    ):  # Try to save ourself from overreporting errors
        logging.info(
            repr((t, t.line, t.end_line, t.column, t.end_column))
        )
        accepts = e.puppet.accepts()
        while frozenset(accepts) in _SOLUTIONS:
            tt = _SOLUTIONS[frozenset(accepts)]
            nt = Token.new_borrow_pos(tt, "<fill_token>", t)
            e.puppet.feed_token(nt)
            accepts = e.puppet.accepts()
        if "_NL" not in accepts:
            logging.warning(
                "Unknown error situation with accepts: "
                + str(accepts)
            )
        e.puppet.feed_token(t)
    return True


bad_char_re = re.compile("[^']", re.U)


def on_character_error(
        e: UnexpectedCharacters, text:str,  diagnostics: List[Diagnostic]
):
    bad_char = text[e.pos_in_stream] 
    if bad_char != "'":
        message = f"Unexpected character '{bad_char}' "
    else:
        message = f'Unexpected character "{bad_char}" '

    if e.allowed:
        message += "Expecting %s" % e.allowed

    diagnostics.append(
        Diagnostic(
            Range(
                Position(e.line - 1, e.column - 1),
                Position(e.line, e.column - 1),
            ),
            message,
        )
    )
    return True


def on_error(e, text: str ,diagnostics: List[Diagnostic]):
    if isinstance(e, UnexpectedToken):
        on_token_error(e, diagnostics)
    elif isinstance(e, UnexpectedCharacters):
        on_character_error(e,text,  diagnostics)
    return True


def get_diagnostics(doctext: str):
    diagnostics: List[Diagnostic] = []
    error_function = lambda error: on_error(error, doctext, diagnostics)
    try:
        lark_grammar_parser.parse(doctext, on_error=error_function)
    except Exception:
        logging.exception("parser raised exception")
        diagnostics.append(
            Diagnostic(
                Range(Position(0, 0), Position(20, 20)),
                "Unknow error on language server, check log",
            )
        )
    return diagnostics
